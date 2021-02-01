import datetime
import json
from abc import ABCMeta

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.forms.models import model_to_dict

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
    Stage, Subject, HoursPerTeacherInClass, Assignment, Room
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


class SubstitutionSummaryView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/substitution_summary.html'


class WeekReplicationConflictWrapperView(UserPassesTestMixin, View, metaclass=ABCMeta):
    """
    This class is a wrapper for the two views that handle week replication:
    in particular, only one static method is implemented, which handles the retrival of
    conflicts for courses, teachers and rooms.
    """
    @staticmethod
    def get_course_teacher_room_conflict(assignments_qs, from_date, to_date, check_course_conflicts):
        """
        This method returns, given a queryset of assignments to duplicate, and an interval of dates
        when to duplicate the assignments, all the conflicts for courses, teachers and rooms.
        In particular: a conflict for teachers may happen when the same teacher is already teaching in some other
        courses at any time of replication of the assignment. A course conflict may happen if the course is
        already busy at any time of the replication of the assignment. A room conflict may happen if its capacity
        is exceeded. Note that the capacity of the room is not counted simply with the number of assignments in the
        same hour-slot, but rather for different courses in the same hour-slot (so if 3 teachers are concurrently in the
        same course in the same room, they are counted as 1).
        If a copy of the assignment that are replicated is already present in the time interval, then it is not
        counted as a conflict (it gets simply ignored).

        Args:
            assignments_qs: queryset of assignments that are going to be replicated
            from_date: date of beginning of interval
            to_date: date of end of interval
            check_course_conflicts: bool to decide if course conflicts should be reported or not
        """
        course_conflicts = Assignment.objects.none()
        teacher_conflicts = Assignment.objects.none()
        room_conflicts = Assignment.objects.none()

        # Define all the possible assignments that can conflict with the replicating assignments
        # we exclude at the beginning the assignments already replicated, in order to avoid false conflicts
        possible_conflicts = Assignment.objects.filter(date__gte=from_date, date__lte=to_date)
        non_conflicts_assign = []
        for a in assignments_qs:
            # Exclude lectures that are equivalent to the one that we want to replicate, since aren't conflicts
            # but the same lecture already defined by the user
            non_conflicts_assign += possible_conflicts.filter(school=a.school,
                                                              school_year=a.school_year,
                                                              course=a.course,
                                                              teacher=a.teacher,
                                                              subject=a.subject,
                                                              # _week_day returns dates Sun-Sat (1,7), while weekday (Mon, Sun) (0,6)
                                                              date__week_day=(a.date.weekday() + 2) % 7,
                                                              hour_start=a.hour_start,
                                                              hour_end=a.hour_end,
                                                              bes=a.bes,
                                                              co_teaching=a.co_teaching,
                                                              absent=a.absent,
                                                              substitution=a.substitution)\
                                                        .values_list('id', flat=True).distinct()

        possible_conflicts = possible_conflicts.exclude(id__in=non_conflicts_assign)

        for a in assignments_qs:
            # Return all assignments from the same course or teacher that would collide in the future.
            # excluding the assignment in the url.
            conflicts = possible_conflicts.filter(school=a.school,
                                                  school_year=a.school_year,
                                                  # _week_day returns dates Sun-Sat (1,7), while weekday (Mon, Sun) (0,6)
                                                  date__week_day=(a.date.weekday() + 2) % 7,
                                                  hour_start=a.hour_start)

            if check_course_conflicts:
                course_conflicts |= conflicts.filter(course=a.course)
            teacher_conflicts |= conflicts.filter(teacher=a.teacher)

            # Check both that the room is not null, and is the same as the current room!
            conf_room = conflicts.filter(room__isnull=False, room=a.room, substitution=False)
            # TODO: This will be super slow!
            for date in conflicts.values_list('date').distinct():
                # Select the distinct courses for the same date
                distinct_course_in_date = conf_room.filter(date=date[0]).values_list('course', flat=True).distinct()
                if a.room is not None and \
                        a.course.id not in distinct_course_in_date and \
                        distinct_course_in_date.count() >= a.room.capacity:
                    # If there is a room in the current assignment,
                    # the course is not one of the already present in the course
                    # and the capacity of the room is filled, then: mark the room conflict.
                    conf_rooms_in_conflicting_dates = conf_room.filter(date=date[0])
                    room_conflicts |= conf_rooms_in_conflicting_dates

        return course_conflicts, teacher_conflicts, room_conflicts


class CheckWeekReplicationView(WeekReplicationConflictWrapperView):
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
        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)
        try:
            without_substitutions = json.loads(self.request.POST.get('without_substitutions', 'false'))
            # If we don't want to automatically delete the extra lectures we should report them as course conflicts
            check_course_conflicts = not json.loads(self.request.POST.get('remove_extra_ass', 'false'))
            assignments_qs = Assignment.objects.filter(id__in=assignments)
        except ObjectDoesNotExist:
            return HttpResponse(_("One of the assignments specified doesn't exist"), 400)

        if without_substitutions:  # the user doesn't want to replicate substitutions
            assignments_qs = assignments_qs.exclude(substitution=True)
        course_conflicts, teacher_conflicts, room_conflicts = self.get_course_teacher_room_conflict(
            assignments_qs, from_date, to_date, check_course_conflicts)
        data = dict(course_conflicts=course_conflicts,
                    teacher_conflicts=teacher_conflicts,
                    room_conflicts=room_conflicts)
        serializer = ReplicationConflictsSerializer(data=data, context={'request': request})
        serializer.is_valid()     # Not sure it is the right way of doing things
        return JsonResponse(serializer.data)



class ReplicateWeekAssignmentsView(WeekReplicationConflictWrapperView):
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
        without_substitutions = json.loads(self.request.POST.get('without_substitutions', 'false'))
        # States if we should remove the non-conflicting assignments already present in the target week
        remove_extra_ass = json.loads(self.request.POST.get('remove_extra_ass', 'false'))
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
            # Check if there are conflicts
            assignments_qs = Assignment.objects.filter(id__in=assignments)

            if without_substitutions:  # the user doesn't want to replicate substitutions
                assignments_qs = assignments_qs.exclude(substitution=True)

            # Get the possible conflicts for course, teachers and rooms.
            # If we don't want to automatically delete the extra lectures we should report them as course conflicts
            course_conflicts, teacher_conflicts, room_conflicts = self.get_course_teacher_room_conflict(
                assignments_qs, from_date, to_date, check_course_conflicts=not remove_extra_ass)

            if len(course_conflicts) > 0 or len(teacher_conflicts) > 0 or len(room_conflicts) > 0:
                # There are conflicts!
                return JsonResponse(
                    AssignmentSerializer((course_conflicts | teacher_conflicts | room_conflicts).distinct(),
                                         context={'request': request}, many=True).data,
                    safe=False, status=400)

            # Delete the assignments of that course in the specified period of time
            school = utils.get_school_from_user(request.user)

            assign_to_del = Assignment.objects.none()
            if remove_extra_ass:
                assign_to_del = Assignment.objects.filter(school=school,
                                                          course=course_pk,
                                                          school_year=school_year_pk,
                                                          date__gte=from_date,
                                                          date__lte=to_date). \
                    exclude(id__in=assignments)  # avoid removing replicating assignments

            assign_to_del.delete()

            # Replicate the assignments
            assignments_list = []
            for a in assignments_qs:
                d = from_date
                while d <= to_date:
                    if d != a.date and d.weekday() == a.date.weekday() and not \
                            Holiday.objects.filter(school=a.school,
                                                   school_year=a.school_year,
                                                   date_end__gte=d,
                                                   date_start__lte=d).exists() and not \
                            Stage.objects.filter(school=a.school,
                                                 school_year=a.school_year,
                                                 date_start__lte=d,
                                                 date_end__gte=d,
                                                 course=a.course):
                        # Found the correct day of the week when to duplicate the assignment
                        new_a = Assignment(
                            teacher=a.teacher,
                            course=a.course,
                            subject=a.subject,
                            room=a.room,
                            hour_start=a.hour_start,
                            hour_end=a.hour_end,
                            bes=a.bes,
                            co_teaching=a.co_teaching,
                            substitution=a.substitution,
                            absent=(False if without_substitutions else a.absent),
                            date=d
                        )
                        new_a_dict = model_to_dict(new_a, exclude=['id'])
                        # Add the new assignment only if is not already present
                        if not Assignment.objects.filter(**new_a_dict).exists():
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

        context['school_years'] = SchoolYear.objects.all().order_by('-year_start')
        return context


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


class DownloadTeacherSubstitutionTicketView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def get(self, request, *args, **kwargs):
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
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='text_bold', fontName="Helvetica-Bold", fontSize=7, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='text_small', fontName="Helvetica", fontSize=4, alignment=TA_CENTER,
                                      borderPadding=0, leading=4))
            title_style = styles['title_style']
            text_bold = styles['text_bold']

            table = [
                [_("Substitute teacher"), Paragraph(str(assignment.teacher), style=text_bold)],
                [_("Date"), Paragraph(str(assignment.date), style=text_bold)],
                [_("Course"), Paragraph(str(assignment.course), style=text_bold)],
                [_("Hour slot"), Paragraph(str(assignment.hour_start) + ' - ' + str(assignment.hour_end), style=text_bold)],
                [_("Subject"), Paragraph(assignment.subject.name, style=text_bold)],
                [_("Room"), Paragraph(str(assignment.room.name) if assignment.room is not None else '', style=text_bold)],
            ]

            elements = [
                Paragraph(_("Substitution ticket"), title_style),
                Spacer(0, 6),
                Spacer(0, 12)
            ]
            t = Table(table)

            t.setStyle(TableStyle(
                [
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ]))

            elements.append(t)

            doc.build(elements)

            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename='substitution.pdf')

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
