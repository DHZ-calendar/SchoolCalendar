from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect, reverse

from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from django.views import View
from django.utils.translation import gettext as _

import io
from django.http import FileResponse, HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from timetable.mixins import AdminSchoolPermissionMixin, SuperUserPermissionMixin, TeacherPermissionMixin

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment

from timetable import utils


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
