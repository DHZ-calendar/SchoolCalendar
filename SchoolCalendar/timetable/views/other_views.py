import datetime

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, reverse

from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from django.views import View
from django.utils.translation import gettext as _

import io
from django.http import FileResponse, HttpResponse, JsonResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from timetable.mixins import AdminSchoolPermissionMixin, SuperUserPermissionMixin, TeacherPermissionMixin
from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment
from timetable import utils
from timetable.serializers import ReplicationConflictsSerializer, AssignmentSerializer


class TimetableView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateView):
    template_name = 'timetable/timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all()
        return context


class SubstituteTeacherView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateView):
    template_name = 'timetable/substitute_teacher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all()
        return context


class TeacherTimetableView(LoginRequiredMixin, TeacherPermissionMixin, TemplateView):
    template_name = 'timetable/teacher_timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all()
        return context


class TeacherReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, TemplateView):
    template_name = 'timetable/teacher_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['teachers_report'] = utils.get_teachers_hours_info()
        return context


class TeacherPDFReportView(LoginRequiredMixin, AdminSchoolPermissionMixin, View):
    def get(self, request, *args, **kwargs):
        teachers_report = utils.get_teachers_hours_info()

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='title_style', fontName="Helvetica-Bold", fontSize=12, leftIndent=200))
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

        for assign in assignments:
            if not (utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
               Assignment.objects.get(id=assign).school == utils.get_school_from_user(self.request.user)):
                return False
        return True

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
            for assign in assignments:
                a = Assignment.objects.get(pk=assign)
                # Return all assignments from the same course or teacher that would collide in the future.
                # excluding the assignment in the url.
                conflicts = Assignment.objects.filter(school_year=a.school_year,
                                                      # _week_day returns dates Sun-Sat (1,7), while weekday (Mon, Sun) (0,6)
                                                      date__week_day=(a.date.weekday() + 2) % 7,
                                                      hour_start=a.hour_start) \
                    .filter(date__gte=from_date, date__lte=to_date) \
                    .exclude(id=a.pk)
                course_conflicts |= conflicts.filter(course=a.course)
                teacher_conflicts |= conflicts.filter(teacher=a.teacher)

            data = dict(course_conflicts=course_conflicts, teacher_conflicts=teacher_conflicts)
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
            if not(utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
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
                # TODO: is the sentence above correctly? Why is it not true for the same class? Because of overriding?
                conflicts = Assignment.objects.filter(school=a.school,
                                                      teacher=a.teacher,
                                                      school_year=a.school_year,
                                                      hour_start=a.hour_start,
                                                      hour_end=a.hour_end,
                                                      date__week_day=((a.date.weekday() + 2) % 7),
                                                      date__gte=from_date,
                                                      date__lte=to_date).exclude(id=a.id)
                if conflicts:
                    # There are conflicts!
                    return JsonResponse(
                        AssignmentSerializer(conflicts, context={'request': request}, many=True).data,
                        safe=False, status=400)

            # delete the assignments of that course in the specified period of time
            school = utils.get_school_from_user(request.user)
            assign_to_del = Assignment.objects.filter(school=school,
                                                      course=course_pk,
                                                      school_year=school_year_pk,
                                                      date__gte=from_date,
                                                      date__lte=to_date).\
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
                            school_year=a.school_year,
                            school=a.school,
                            hour_start=a.hour_start,
                            hour_end=a.hour_end,
                            bes=a.bes,
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
        email = kwargs.get('email')
        utils.send_invitation_email(email, request)
        return HttpResponse(status=200)


class SendInvitationAdminSchoolEmailView(LoginRequiredMixin, SuperUserPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        email = kwargs.get('email')
        utils.send_invitation_email(email, request)
        return HttpResponse(status=200)
