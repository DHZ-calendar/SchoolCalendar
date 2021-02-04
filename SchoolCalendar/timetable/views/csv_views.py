import pandas as pd
import datetime

from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

from rest_pandas import PandasSimpleView, PandasExcelRenderer
from timetable import utils
from timetable.permissions import SchoolAdminCanWriteDelete
from timetable.models import HourSlot, Assignment, Teacher, Course, Room

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


class TimetableTeacherCSVReportViewSet(PandasSimpleView):
    queryset = Teacher.objects.none()  # needed to avoid throwing errors
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]  # In the meantime only school admin.
    renderer_classes = [PandasExcelRenderer]

    def get_pandas_filename(self, request, format):
        return str(self.teacher) + " - " + self.monday_date.strftime("%d-%m-%Y")

    def get_data(self, request, *args, **kwargs):
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


class TimetableCourseCSVReportViewSet(PandasSimpleView):
    queryset = Teacher.objects.none()  # needed to avoid throwing errors
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]  # In the meantime only school admin.
    renderer_classes = [PandasExcelRenderer]

    def get_pandas_filename(self, request, format):
        return str(self.course) + " - " + self.monday_date.strftime("%d-%m-%Y")

    def get_data(self, request, *args, **kwargs):
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


class TimetableRoomCSVReportViewSet(PandasSimpleView):
    renderer_classes = [PandasExcelRenderer]
    queryset = Teacher.objects.none()  # needed to avoid throwing errors
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]    # In the meantime only school admin.

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


class GeneralTimetablePandasExcelRenderer(PandasExcelRenderer):
    def get_pandas_kwargs(self, data, renderer_context):
        return {'index_label': _('Teacher')}  # Here we set the label of the teacher column


class TimetableGeneralCSVReportViewSet(PandasSimpleView):
    renderer_classes = [GeneralTimetablePandasExcelRenderer]
    queryset = Teacher.objects.none()  # needed to avoid throwing errors
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]    # In the meantime only school admin.

    def get_pandas_filename(self, request, format):
        return _("General") + " - " + self.monday_date.strftime("%d-%m-%Y")

    def get_data(self, request, *args, **kwargs):
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

        for h in hours_assign:
            if h not in hours_list:
                hours_list.append(h)

        nr_teachers = assignments.values('teacher__id').distinct()
        queryset = [{} for i in nr_teachers]

        dow_with_hour_slots = [d + "_" + str(i) for d in days_of_week for i in range(len(hours_list))]
        for i in queryset:
            i.update({j: '' for j in dow_with_hour_slots})

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

            field = days_of_week[assign.date.weekday()] + "_" +  str(hs_idx)
            queryset[teacher_idx][field] = "{} {}".format(str(assign.course.year), assign.course.section)

        df = pd.DataFrame(queryset)
        # Set the index for the df to teacher, so that we can drop the counter of rows.
        df.set_index(['teacher'], inplace=True)
        # Create subcolumns, so that the dow will be the super column of the hours
        df.columns = pd.MultiIndex.from_tuples([c.split('_') for c in df.columns])
        # Rename both the index and the columns with reasonable human-readable names.
        general_labels = {
            'teacher': _('Teacher')
        }
        general_labels.update(labels)
        for i in range(len(hours_list)):
            general_labels.update({str(i): str(i + 1)})
        df.rename(columns=general_labels, inplace=True)

        return df


class SubstitutionsCSVReportViewSet(PandasSimpleView):
    renderer_classes = [PandasExcelRenderer]
    queryset = Assignment.objects.none()  # needed to avoid throwing errors
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]    # In the meantime only school admin.

    def get_pandas_filename(self, request, format):
        return _('Substitutions')

    def get_data(self, request, *args, **kwargs):
        try:
            school_year = kwargs.get('school_year_pk')
            school = utils.get_school_from_user(self.request.user)
        except ValueError:
            return []

        assignments = Assignment.objects.filter(school=school,
                                                school_year=school_year,
                                                substitution=True) \
                                    .order_by('-date', 'hour_start', 'hour_end') \
                                    .values('date', 'hour_start', 'hour_end', 'course__year', 'course__section',
                                            'subject__name', 'room__name', 'bes', 'co_teaching',
                                            'teacher__first_name', 'teacher__last_name',
                                            'substituted_assignment__teacher__last_name',
                                            'substituted_assignment__teacher__first_name', 'free_substitution')

        df = pd.DataFrame(assignments)
        df['substitution_teacher'] = df['teacher__last_name'] + " " + df['teacher__first_name']
        del df['teacher__last_name']
        del df['teacher__first_name']
        df['absent_teacher'] = df['substituted_assignment__teacher__last_name'] + " " + df['substituted_assignment__teacher__first_name']
        del df['substituted_assignment__teacher__last_name']
        del df['substituted_assignment__teacher__first_name']
        # Set the hour format to hh:mm
        df['hour_start'] = df['hour_start'].apply(lambda x: x.strftime('%H:%M'))
        df['hour_end'] = df['hour_end'].apply(lambda x: x.strftime('%H:%M'))
        # Set the date format
        df['date'] = df['date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        # Set the boolean formats
        df['free_substitution'] = df['free_substitution'].apply(lambda x: _('True') if x else _('False'))
        df['bes'] = df['bes'].apply(lambda x: _('True') if x else _('False'))
        df['co_teaching'] = df['co_teaching'].apply(lambda x: _('True') if x else _('False'))
        # Rename both the index and the columns with reasonable human-readable names.
        subst_labels = {
            'date': _('Date'),
            'course__year': _('Course year'),
            'course__section': _('Course section'),
            'substitution_teacher': _('Substitution teacher'),
            'absent_teacher': _('Absent teacher'),
            'free_substitution': _('Free substitution'),
            'subject__name': _('Subject'),
            'room__name': _('Room'),
            'bes': _('B.E.S.'),
            'co_teaching': _('Co-teaching')
        }
        subst_labels.update(labels)
        df.rename(columns=subst_labels, inplace=True)

        return df
