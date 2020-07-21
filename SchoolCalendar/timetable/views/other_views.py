import datetime

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from django.views import View
from django.utils.translation import gettext as _

import io
from django.http import FileResponse, HttpResponse, JsonResponse
from reportlab.graphics.shapes import String

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from timetable.mixins import AdminSchoolPermissionMixin, SuperUserPermissionMixin, TeacherPermissionMixin
from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment
from timetable import utils
from timetable.serializers import ReplicationConflictsSerializer, AssignmentSerializer, SubstitutionSerializer
from timetable.views.CRUD_views import TemplateViewWithSchoolYears


class TimetableView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/timetable.html'


class SubstituteTeacherView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/substitute_teacher.html'


class TeacherTimetableView(LoginRequiredMixin, TeacherPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/teacher_timetable.html'


class RoomTimetableView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/room_timetable.html'


class TeacherSummaryView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/teacher_summary.html'


class CourseSummaryView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/course_summary.html'


class TeacherPDFReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def get(self, request, *args, **kwargs):
        school = utils.get_school_from_user(self.request.user)
        teachers_report = utils.get_teachers_hours_info(school)

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER))
        title_style = styles['title_style']
        elements = [
            Paragraph(_("Teachers report"), title_style),
            Spacer(0, 12)
        ]

        headers = [_('Last name'), _('First name'), _('Subject'), _('Course'), _('Teaching hours made'),
                   _('Substitution hours made'), _('B.E.S. hours made'), _('Missing teaching hours'),
                   _('Missing B.E.S. hours')]
        headers = map(lambda h: '\n'.join(h.split(' ')), headers)  # To avoid breaking page borders
        data = [headers] + \
               [[
                   Paragraph(str(teacher[key]), styles['Normal']) for key in teacher.keys()
               ] for teacher in teachers_report]
        t = Table(data)

        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        elements.append(t)

        doc.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='report.pdf')


class CheckWeekReplicationView(UserPassesTestMixin, View):
    def test_func(self):
        assignments = self.request.POST.getlist('assignments[]')
        if not (utils.is_adminschool(self.request.user)):
            return False
        school = utils.get_school_from_user(self.request.user)

        # They should be in the same school of the admin and all of them should exist
        return Assignment.objects.filter(id__in=assignments, school=school).count() == len(assignments)

    def post(self, request, *args, **kwargs):
        """
        Check conflicts with the assignments of a week if repeated in a specific date range
        """
        assignments = request.POST.getlist('assignments[]')
        try:
            from_date = datetime.datetime.strptime(kwargs.get('from'), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(kwargs.get('to'), '%Y-%m-%d').date()
            course_conflicts = Assignment.objects.none()
            teacher_conflicts = Assignment.objects.none()
            room_conflicts = Assignment.objects.none()
            for assign in assignments:
                a = Assignment.objects.get(pk=assign)
                # Return all assignments from the same course or teacher that would collide in the future.
                # excluding the assignment in the url.
                conflicts = Assignment.objects.filter(course__school_year=a.course.school_year,
                                                      # _week_day returns dates Sun-Sat (1,7), while weekday (Mon, Sun) (0,6)
                                                      date__week_day=(a.date.weekday() + 2) % 7,
                                                      hour_start=a.hour_start) \
                    .filter(date__gte=from_date, date__lte=to_date) \
                    .exclude(id=a.pk)
                course_conflicts |= conflicts.filter(course=a.course)
                teacher_conflicts |= conflicts.filter(teacher=a.teacher)

                # Check both that the room is not null, and is the same as the current room!
                conf_room = conflicts.filter(room__isnull=False, room=a.room, substitution=False)
                if a.room is not None and conf_room.count() >= a.room.capacity:
                    room_conflicts |= conf_room

            data = dict(course_conflicts=course_conflicts,
                        teacher_conflicts=teacher_conflicts,
                        room_conflicts=room_conflicts)
            serializer = ReplicationConflictsSerializer(data=data, context={'request': request})
            serializer.is_valid()
            return JsonResponse(serializer.data)
        except ObjectDoesNotExist:
            return HttpResponse(_("One of the assignments specified doesn't exist"), 400)


class ReplicateWeekAssignmentsView(UserPassesTestMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin, and it is replicating the assignments that
        are in the correct school
        :return:
        """
        assignments = self.request.POST.getlist('assignments[]')

        for assign in assignments:
            if not (utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
                    Assignment.objects.get(id=assign).school == utils.get_school_from_user(self.request.user)):
                return False
        return True

    def post(self, request, *args, **kwargs):
        """
        Create multiple instances of the assignments of a week in a given time period

        :param request:
        :return:
        """
        assignments = self.request.POST.getlist('assignments[]')
        try:
            from_date = datetime.datetime.strptime(kwargs.get('from'), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(kwargs.get('to'), '%Y-%m-%d').date()
            school_year_pk = kwargs.get('school_year_pk')
            course_pk = kwargs.get('course_pk')
        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)

        if from_date > to_date:
            # From date should be smaller than to_date
            return HttpResponse(_('The beginning of the period is greater then the end of the period'), 400)
        try:
            # check if there are conflicts
            for assign in assignments:
                a = Assignment.objects.get(id=assign)

                # There can't be conflicts among the newly created assignments and the teaching hours of the same teacher!
                # The same is not true for conflicts of the same class.
                conflicts = Assignment.objects.filter(school=a.school,
                                                      course__school_year=a.course.school_year,
                                                      hour_start=a.hour_start,
                                                      hour_end=a.hour_end,
                                                      date__week_day=((a.date.weekday() + 2) % 7),
                                                      date__gte=from_date,
                                                      date__lte=to_date). \
                    exclude(id=a.id). \
                    filter(Q(teacher=a.teacher) | Q(room__isnull=False, room=a.room))
                if conflicts.filter(teacher=a.teacher) or (
                        a.room is not None and conflicts.filter(room=a.room).count() >= a.room.capacity
                ):
                    # There are conflicts!
                    return JsonResponse(
                        AssignmentSerializer(conflicts, context={'request': request}, many=True).data,
                        safe=False, status=400)

            # delete the assignments of that course in the specified period of time
            school = utils.get_school_from_user(request.user)
            assign_to_del = Assignment.objects.filter(school=school,
                                                      course=course_pk,
                                                      course__school_year=school_year_pk,
                                                      date__gte=from_date,
                                                      date__lte=to_date). \
                exclude(id__in=assignments)  # avoid removing replicating assignments
            assign_to_del.delete()

            # replicate the assignments
            assignments_list = []
            for assign in assignments:
                d = from_date
                a = Assignment.objects.get(id=assign)
                while d <= to_date:
                    if d != a.date and d.weekday() == a.date.weekday() and not \
                            Holiday.objects.filter(school=a.school,
                                                   school_year=a.course.school_year,
                                                   date_end__gte=d,
                                                   date_start__lte=d).exists() and not \
                            Stage.objects.filter(school=a.school,
                                                 course__school_year=a.course.school_year,
                                                 date_start__lte=d,
                                                 date_end__gte=d,
                                                 course=a.course):
                        # Found the correct day of the week when to duplicate the assignment
                        new_a = Assignment(
                            teacher=a.teacher,
                            course=a.course,
                            subject=a.subject,
                            room=a.room,
                            school=a.school,
                            hour_start=a.hour_start,
                            hour_end=a.hour_end,
                            bes=a.bes,
                            co_teaching=a.co_teaching,
                            substitution=a.substitution,
                            absent=a.absent,
                            date=d
                        )
                        assignments_list.append(new_a)
                    d += datetime.timedelta(days=1)

            # Create with one single query.
            Assignment.objects.bulk_create(assignments_list)
            return HttpResponse(status=201)
        except ObjectDoesNotExist:
            return HttpResponse(_("One of the Assignments specified doesn't exist"), 404)


class TeacherSubstitutionView(UserPassesTestMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin, and it is substituting the assignment that
        are in the correct school
        :return:
        """
        assign = self.kwargs.get('assignment_pk')

        if not (utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
                Assignment.objects.get(id=assign).school == utils.get_school_from_user(self.request.user)):
            return False

        if not Assignment.objects.filter(id=assign,
                                         school=utils.get_school_from_user(self.request.user).id).exists():
            return False
        return True

    def get(self, request, *args, **kwargs):
        # Return all teachers for a certain school.
        # May need to add only teachers for which there is at least one hour_per_teacher_in_class instance in
        # the given school_year
        request.assignment_pk = self.kwargs.get('assignment_pk')

        school = utils.get_school_from_user(self.request.user)

        a = Assignment.objects.get(id=self.kwargs.get('assignment_pk'),
                                   school=school.id)

        teachers_list = utils.get_available_teachers(a, school)

        # Show all the other teachers (the ones that may be busy or have an absence block).
        other_teachers = Teacher.objects.filter(school=school) \
            .exclude(id__in=teachers_list.values('id')) \
            .exclude(id=a.teacher.id)  # Exclude the teacher herself!

        data = dict(available_teachers=teachers_list,
                    other_teachers=other_teachers)
        serializer = SubstitutionSerializer(data=data, context={'request': request})
        serializer.is_valid()
        return JsonResponse(serializer.data)


class SubstituteTeacherApiView(UserPassesTestMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin, it is substituting the assignments that
        are in the correct school and the teacher is in the same school too.
        :return:
        """
        assign = self.kwargs.get('assignment_pk')
        teacher = self.kwargs.get('teacher_pk')
        school = utils.get_school_from_user(self.request.user)

        if not (utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
                Assignment.objects.get(id=assign).school == school):
            return False

        if not Teacher.objects.filter(id=teacher, school=school.id).exists():
            return False
        return True

    def post(self, request, *args, **kwargs):
        # Insert the substitution assignment
        assign = self.kwargs.get('assignment_pk')
        teacher = self.kwargs.get('teacher_pk')
        school = utils.get_school_from_user(self.request.user)

        a = Assignment.objects.get(id=assign,
                                   school=school.id)
        teachers_list = utils.get_available_teachers(a, school)
        other_teachers = Teacher.objects.filter(school=school).exclude(id__in=teachers_list.values('id'))

        new_assign = Assignment(
            teacher=Teacher.objects.get(id=teacher),
            course=a.course,
            subject=a.subject,
            school=a.school,
            room=a.room,
            date=a.date,
            hour_start=a.hour_start,
            hour_end=a.hour_end,
            bes=a.bes,
            co_teaching=a.co_teaching,
            substitution=True,
            absent=False,
            free_substitution=False
        )

        if teachers_list.filter(id=teacher).exists():
            # The substitution counts and it's a normal one
            a.absent = True
        elif other_teachers.filter(id=teacher).exists():
            # The substitution does not count
            new_assign.free_substitution = True
        else:
            return HttpResponse(_("The teacher is not valid!"), 400)

        a.save()
        new_assign.save()
        return HttpResponse(status=200)


class TimetableReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateView):
    template_name = 'timetable/timetable_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all()
        return context


class TimetableTeacherPDFReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin, the teacher exists and is in the same school.
        :return:
        """
        school_year = self.kwargs.get('school_year_pk')
        teacher = self.kwargs.get('teacher_pk')
        school = utils.get_school_from_user(self.request.user)

        if not (utils.is_adminschool(self.request.user) and SchoolYear.objects.filter(id=school_year).exists()):
            return False

        if not Teacher.objects.filter(id=teacher, school=school.id).exists():
            return False
        return True

    def get(self, request, *args, **kwargs):
        try:
            school_year = kwargs.get('school_year_pk')
            teacher = kwargs.get('teacher_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(request.user)
        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER))
        title_style = styles['title_style']

        table = []
        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year, teacher=teacher,
                                                date__gte=monday_date, date__lte=end_date)
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        for lecture in hours_assign:
            table.append(
                [lecture] + [''] * 6
            )

        for i, slot in enumerate(hours_hour_slots):
            found = False
            for row in table:
                if row[0]['hour_start'] == slot['hour_start'] and \
                        row[0]['hour_end'] == slot['hour_end']:
                    found = True
                    break
            if not found:
                table.insert(i,
                             [slot] + [''] * 6
                             )

        for assign in assignments:
            for row in table:
                if row[0]['hour_start'] == assign.hour_start and \
                        row[0]['hour_end'] == assign.hour_end:
                    day_of_week = assign.date.weekday()
                    row[day_of_week + 1] = [
                        Paragraph(str(assign.subject), styles['Normal']),
                        Paragraph(str(assign.course.year) + ' ' + str(assign.course.section), styles['Normal'])
                    ]
                    break

        # format the hours of the row
        for row in table:
            row[0] = row[0]['hour_start'].strftime("%H:%M") + '\n' + row[0]['hour_end'].strftime("%H:%M")

        teacher = Teacher.objects.get(id=teacher)
        elements = [
            Paragraph(_("Teacher timetable"), title_style),
            Spacer(0, 6),
            Paragraph(_('Teacher') + ': ' + str(teacher), styles['Normal']),
            Paragraph(_('Week of') + ': ' + monday_date.strftime("%d/%m/%Y") + ' - ' +
                      end_date.strftime("%d/%m/%Y"), styles['Normal']),
            Spacer(0, 12)
        ]

        headers = ['', _('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday')]
        data = [headers] + table
        t = Table(data)

        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        elements.append(t)

        doc.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=str(teacher) + '.pdf')


class TimetableCoursePDFReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin and the Course exists and is in the same school.
        :return:
        """
        school_year = self.kwargs.get('school_year_pk')
        course = self.kwargs.get('course_pk')
        school = utils.get_school_from_user(self.request.user)

        if not (utils.is_adminschool(self.request.user) and SchoolYear.objects.filter(id=school_year).exists()):
            return False

        if not Course.objects.filter(id=course, school=school.id, school_year=school_year).exists():
            return False
        return True

    def get(self, request, *args, **kwargs):
        try:
            school_year = kwargs.get('school_year_pk')
            course = self.kwargs.get('course_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(request.user)
        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='text_bold', fontName="Helvetica-Bold", fontSize=10))
        title_style = styles['title_style']

        table = []
        hour_slots = HourSlot.objects.filter(school=school, school_year=school_year)
        hours_hour_slots = hour_slots.extra(
            select={
                'hour_start': 'starts_at',
                'hour_end': 'ends_at'
            }
        ).order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()
        assignments = Assignment.objects.filter(school=school, course__school_year=school_year, course=course,
                                                date__gte=monday_date, date__lte=end_date)
        hours_assign = assignments.order_by('hour_start', 'hour_end').values('hour_start', 'hour_end').distinct()

        for lecture in hours_assign:
            table.append(
                [lecture] + [''] * 6
            )

        for i, slot in enumerate(hours_hour_slots):
            found = False
            for row in table:
                if row[0]['hour_start'] == slot['hour_start'] and \
                        row[0]['hour_end'] == slot['hour_end']:
                    found = True
                    break
            if not found:
                table.insert(i,
                             [slot] + [''] * 6
                             )

        for assign in assignments:
            for row in table:
                if row[0]['hour_start'] == assign.hour_start and \
                        row[0]['hour_end'] == assign.hour_end:
                    day_of_week = assign.date.weekday()
                    row[day_of_week + 1] = [
                        Paragraph(str(assign.subject), styles['text_bold']),
                        Paragraph(str(assign.teacher), styles['Normal'])
                    ]
                    break

        # format the hours of the row
        for row in table:
            row[0] = row[0]['hour_start'].strftime("%H:%M") + '\n' + row[0]['hour_end'].strftime("%H:%M")

        course = Course.objects.get(id=course)
        elements = [
            Paragraph(_("Course timetable"), title_style),
            Spacer(0, 6),
            Paragraph(_('Course') + ': ' + str(course), styles['Normal']),
            Paragraph(_('Week of') + ': ' + monday_date.strftime("%d/%m/%Y") + ' - ' +
                      end_date.strftime("%d/%m/%Y"), styles['Normal']),
            Spacer(0, 12)
        ]

        headers = ['', _('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday')]
        data = [headers] + table
        t = Table(data)

        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        elements.append(t)

        doc.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=str(course) + '.pdf')


class TimetableGeneralPDFReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def test_func(self):
        """
        Returns True only when the user logged is an admin and the School Year exists.
        :return:
        """
        school_year = self.kwargs.get('school_year_pk')

        if not (utils.is_adminschool(self.request.user) and SchoolYear.objects.filter(id=school_year).exists()):
            return False

        return True

    def get(self, request, *args, **kwargs):
        try:
            school_year = kwargs.get('school_year_pk')
            monday_date = datetime.datetime.strptime(kwargs.get('monday_date'), '%Y-%m-%d').date()
            end_date = monday_date + datetime.timedelta(days=6)
            school = utils.get_school_from_user(request.user)
        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                                leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='text_bold', fontName="Helvetica-Bold", fontSize=7, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='text_small', fontName="Helvetica", fontSize=4, alignment=TA_CENTER,
                                  borderPadding=0, leading=4))
        title_style = styles['title_style']

        table = []
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

        hours = list(hours_assign)

        for i, slot in enumerate(hours_hour_slots):
            found = False
            for row in hours:
                if row['hour_start'] == slot['hour_start'] and \
                        row['hour_end'] == slot['hour_end']:
                    found = True
                    break
            if not found:
                hours.insert(i, slot)

        teacher_id = None
        for assign in assignments:
            if teacher_id != assign.teacher.id:
                table.append([Paragraph(str(assign.teacher), styles['text_small'])] +
                             [''] * len(hours) * 6)
                teacher_id = assign.teacher.id

            i = 0
            for hour in hours:
                if hour['hour_start'] == assign.hour_start and \
                        hour['hour_end'] == assign.hour_end:
                    break
                i += 1
            column = assign.date.weekday() * i + 1

            table[-1][column] = Paragraph(str(assign.course.year) + ' ' + assign.course.section, styles['text_small'])

        elements = [
            Paragraph(_("General timetable"), title_style),
            Spacer(0, 6),
            Paragraph(_('Week of') + ': ' + monday_date.strftime("%d/%m/%Y") + ' - ' +
                      end_date.strftime("%d/%m/%Y"), styles['Normal']),
            Spacer(0, 12)
        ]

        fill_spaces = [''] * (len(hours) - 1)
        headers = ['', Paragraph(_('Monday'), styles['text_small'])] + fill_spaces + \
                  [Paragraph(_('Tuesday'), styles['text_small'])] + fill_spaces + \
                  [Paragraph(_('Wednesday'), styles['text_small'])] + fill_spaces + \
                  [Paragraph(_('Thursday'), styles['text_small'])] + fill_spaces + \
                  [Paragraph(_('Friday'), styles['text_small'])] + fill_spaces + \
                  [Paragraph(_('Saturday'), styles['text_small'])] + fill_spaces

        days = ['']
        spans = []
        for day in range(6):
            days += [
                Paragraph(str(i + 1), styles['text_small']) for i in range(len(hours))
            ]
            start = 1 + len(hours) * day
            end = start + len(hours) - 1
            spans.append(('SPAN', (start, 0), (end, 0)), )

        data = [headers] + [days] + table
        t = Table(data, colWidths=[None] + [7 * mm] * (len(headers) - 2))

        t.setStyle(TableStyle(
            spans +
            [
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]))

        elements.append(t)

        doc.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=str(monday_date) + '.pdf')


class SendTeacherSubstitutionEmailView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        assign_pk = kwargs.get('assign_pk')
        assignment_to_subst = Assignment.objects.get(id=assign_pk)
        assignment = Assignment.objects.filter(
            course=assignment_to_subst.course,
            subject=assignment_to_subst.subject,
            room=assignment_to_subst.room,
            school=assignment_to_subst.school,
            date=assignment_to_subst.date,
            hour_start=assignment_to_subst.hour_start,
            hour_end=assignment_to_subst.hour_end,
            bes=assignment_to_subst.bes,
            co_teaching=assignment_to_subst.co_teaching,
            substitution=True,
            absent=False
        ).first()
        if assignment:
            subject = 'SchoolCalendar - Substitution assigned'
            html_message = render_to_string('email_templates/substitution.html',
                                            {'user': assignment.teacher, 'assignment': assignment})
            from_email = None
            to = assignment.teacher.email

            send_mail(subject, None, from_email, [to], html_message=html_message, fail_silently=False)
            return HttpResponse(status=200)

        return HttpResponse(status=400)


class LoggedUserRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if utils.is_adminschool(self.request.user):
            return reverse('timetable-view')
        elif self.request.user.is_superuser:
            return reverse('school-listview')
        else:
            return reverse('teacher_timetable-view')


class SendInvitationTeacherEmailView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        user_pk = kwargs.get('user_pk')
        utils.send_invitation_email(user_pk, request)
        return HttpResponse(status=200)


class SendInvitationAdminSchoolEmailView(LoginRequiredMixin, SuperUserPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        user_pk = kwargs.get('user_pk')
        utils.send_invitation_email(user_pk, request)
        return HttpResponse(status=200)
