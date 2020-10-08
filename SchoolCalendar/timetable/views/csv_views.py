import csv
import pandas as pd

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.serializers import CharField
from rest_framework_csv.renderers import CSVRenderer
from django.utils.translation import gettext_lazy as _

import datetime

from rest_pandas import PandasView, PandasSimpleView, PandasExcelRenderer
from timetable import utils
from timetable.permissions import SchoolAdminCanWriteDelete
from timetable.models import HourSlot, Assignment, Teacher, Course, Room

from timetable.csv_serializers import WeekTimetableCSVSerializer, GeneralTimetableCSVSerializer

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

labels = {
            'hour_start': _('Hour start'),
            'hour_end': _('Hour end'),
            'Monday': _('Monday'),
            'Tuesday': _('Tuesday'),
            'Wednesday': _('Wednesday'),
            'Thursday': _('Thursday'),
            'Friday': _('Friday'),
            'Saturday': _('Saturday')
        }


class GenericCSVViewSet(ViewSet):
    renderer_classes = [CSVRenderer]

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = self.serializer_class.Meta.fields
        return context

    def finalize_response(self, request, response, *args, **kwargs):
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(self.get_filename())
        return super().finalize_response(request, response, *args, **kwargs)


class WeekTimetableCSVViewSet(GenericCSVViewSet):
    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['labels'] = {
            'hour_start': _('Hour start'),
            'hour_end': _('Hour end'),
            'Monday': _('Monday'),
            'Tuesday': _('Tuesday'),
            'Wednesday': _('Wednesday'),
            'Thursday': _('Thursday'),
            'Friday': _('Friday'),
            'Saturday': _('Saturday')
        }
        return context


class TimetableTeacherCSVReportViewSet(WeekTimetableCSVViewSet):
    serializer_class = WeekTimetableCSVSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    lookup_url_kwarg = ['teacher_pk', 'school_year_pk', 'monday_date']

    def get_filename(self):
        return str(self.teacher) + " - " + self.monday_date.strftime("%d-%m-%Y")

    def list(self, request, **kwargs):
        """
        """
        try:
            school_year = kwargs.get('school_year_pk')
            teacher_pk = kwargs.get('teacher_pk')
            # TODO: maybe it is better to get Monday date here,
            # rather than letting JS doing the job and giving it for granted?
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(self.request.user)
        except ValueError:
            return []

        self.teacher = Teacher.objects.get(pk=teacher_pk)
        self.monday_date = monday_date

        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year, teacher=teacher_pk,
                                                date__gte=monday_date, date__lte=end_date)
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        hours_list = [h for h in hours_hour_slots]

        for h in hours_assign:
            if h not in hours_list:
                hours_list.append(h)

        queryset = sorted(hours_list, key=lambda x: (x['hour_start'], x['hour_end']))

        for i in queryset:
            i.update({j: '' for j in days_of_week})

        for assign in assignments:
            for hour in queryset:
                if hour['hour_start'] == assign.hour_start and \
                        hour['hour_end'] == assign.hour_end:
                    day_of_week = days_of_week[assign.date.weekday()]
                    hour[day_of_week] = "{} - {} {}".format(str(assign.subject),
                                                            str(assign.course.year), str(assign.course.section))
                    break

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class TimetableCourseCSVReportViewSet(WeekTimetableCSVViewSet):
    serializer_class = WeekTimetableCSVSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    lookup_url_kwarg = ['course_pk', 'school_year_pk', 'monday_date']

    def get_filename(self):
        return str(self.course) + " - " + self.monday_date.strftime("%d-%m-%Y")

    def list(self, request, **kwargs):
        """
        """
        try:
            school_year = kwargs.get('school_year_pk')
            course_pk = self.kwargs.get('course_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(self.request.user)
        except ValueError:
            return []

        self.course = Course.objects.get(pk=course_pk)
        self.monday_date = monday_date

        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year, course=course_pk,
                                                date__gte=monday_date, date__lte=end_date)
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        hours_list = [h for h in hours_hour_slots]

        for h in hours_assign:
            if h not in hours_list:
                hours_list.append(h)

        queryset = sorted(hours_list, key=lambda x: (x['hour_start'], x['hour_end']))

        for i in queryset:
            i.update({j: '' for j in days_of_week})

        for assign in assignments:
            for hour in queryset:
                if hour['hour_start'] == assign.hour_start and \
                        hour['hour_end'] == assign.hour_end:
                    day_of_week = days_of_week[assign.date.weekday()]

                    if assign.bes:
                        assignment_text = _('B.E.S.')
                    elif assign.co_teaching:
                        assignment_text = _('Co-teaching')
                    else:
                        assignment_text = str(assign.subject)

                    assignment_text += " - " + str(assign.teacher)
                    if assign.room:
                        assignment_text += " (" + assign.room.name + ")"

                    if hour[day_of_week] != '':
                        hour[day_of_week] += "\n\n"
                    hour[day_of_week] += assignment_text
                    break

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class TimetableRoomCSVReportViewSet(PandasSimpleView):
    renderer_classes = [PandasExcelRenderer]
    queryset = Teacher.objects.none()  # needed to avoid throwing errors

    def get_pandas_filename(self, request, format):
        return str(self.room) + " - " + self.monday_date.strftime("%d-%m-%Y")

    def get_data(self, request, *args, **kwargs):
        try:
            school_year = kwargs.get('school_year_pk')
            room_pk = self.kwargs.get('room_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(self.request.user)
        except ValueError:
            return []

        self.room = Room.objects.get(pk=room_pk)
        self.monday_date = monday_date
        if self.monday_date.weekday() != 0:   # Monday is the weekday 0
            # Set the Monday date to the smaller closest Monday.
            # Correct accordingly the end_date.
            self.monday_date -= datetime.timedelta(days=self.monday_date.weekday())
            end_date = self.monday_date + datetime.timedelta(days=6)

        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year, room=room_pk,
                                                date__gte=monday_date, date__lte=end_date)

        # In case we have special hours slots: take the assignments of the current week, and check that
        # all the related hour_slots appear in hours_list
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        hours_list = [h for h in hours_hour_slots]

        for h in hours_assign:
            if h not in hours_list:
                # Add special hour slots.
                hours_list.append(h)

        queryset = sorted(hours_list, key=lambda x: (x['hour_start'], x['hour_end']))

        for i in queryset:
            i.update({j: '' for j in days_of_week})

        for assign in assignments:
            for hour in queryset:
                if hour['hour_start'] == assign.hour_start and \
                        hour['hour_end'] == assign.hour_end:
                    day_of_week = days_of_week[assign.date.weekday()]

                    if assign.bes:
                        assignment_text = _('B.E.S.')
                    elif assign.co_teaching:
                        assignment_text = _('Co-teaching')
                    else:
                        assignment_text = str(assign.subject)

                    assignment_text += " - {} - {} {}".format(str(assign.teacher),
                                                              str(assign.course.year), str(assign.course.section))

                    if hour[day_of_week] != '':
                        # In case we already have more than one lecture, add a newline.
                        hour[day_of_week] += "\n"
                    hour[day_of_week] += assignment_text
                    break

        df = pd.DataFrame(queryset)
        # Set the hour format to hh:mm
        df['hour_start'] = df['hour_start'].apply(lambda x: x.strftime('%H:%M'))
        df['hour_end'] = df['hour_end'].apply(lambda x: x.strftime('%H:%M'))
        # Set the index for the df to hour_start and hour_end, so that we can drop the counter of rows.
        df.set_index(['hour_start', 'hour_end'], inplace=True)
        # Rename both the index and the columns with reasonable human-readable names.
        df.rename(labels, inplace=True)
        df.index.rename(["".join(labels['hour_start']), "".join(labels['hour_end'])], inplace=True)

        return df


class TimetableGeneralCSVReportViewSet(GenericCSVViewSet):
    serializer_class = GeneralTimetableCSVSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    lookup_url_kwarg = ['school_year_pk', 'monday_date']

    def get_filename(self):
        return _("General") + " - " + self.monday_date.strftime("%d-%m-%Y")

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = self.serializer_class.Meta.fields
        context['labels'] = {
            'teacher': _('Teacher')
        }

        for d in days_of_week:
            start = True
            for i in range(len(self.hours_list)):
                if start:
                    txt = _(d) + " 1"
                    start = False
                else:
                    txt = str(i + 1)
                context['labels'].update({d + str(i): txt})
        return context

    def list(self, request, **kwargs):
        """
        """
        try:
            school_year = kwargs.get('school_year_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(self.request.user)
        except ValueError:
            return []

        self.monday_date = monday_date

        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year,
                                                date__gte=monday_date, date__lte=end_date). \
            order_by('teacher__last_name', 'teacher__first_name')
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        hours_list = [h for h in hours_hour_slots]
        self.hours_list = hours_list

        for h in hours_assign:
            if h not in hours_list:
                hours_list.append(h)

        nr_teachers = assignments.values('teacher__id').distinct()
        queryset = [{} for i in nr_teachers]

        self.dow_with_hour_slots = [d + str(i) for d in days_of_week for i in range(len(hours_list))]
        for i in queryset:
            i.update({j: '' for j in self.dow_with_hour_slots})

        teacher_id, teacher_idx = None, -1
        for assign in assignments:
            if teacher_id != assign.teacher.id:
                teacher_id = assign.teacher.id
                teacher_idx += 1
                queryset[teacher_idx]['teacher'] = str(assign.teacher)

            hs = {
                'hour_start': assign.hour_start,
                'hour_end': assign.hour_end
            }
            hs_idx = hours_list.index(hs)

            field = days_of_week[assign.date.weekday()] + str(hs_idx)
            queryset[teacher_idx][field] = "{} {}".format(str(assign.course.year), assign.course.section)

        serializer = self.serializer_class(queryset, dow_with_hour_slots=self.dow_with_hour_slots, many=True)
        return Response(serializer.data)
