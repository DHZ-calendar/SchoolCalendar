from django.contrib import admin


from timetable.models import AdminSchool, MyUser
from timetable.forms import AdminSchoolForm


class AdminSchoolAdmin(admin.ModelAdmin):

    # def get_form(self, request, *args, **kwargs):
    #     form = AdminSchoolForm(request.user)
    #     return form
    pass


admin.site.register(MyUser)
admin.site.register(AdminSchool, AdminSchoolAdmin)
