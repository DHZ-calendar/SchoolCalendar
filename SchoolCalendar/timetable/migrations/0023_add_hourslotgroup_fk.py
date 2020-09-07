from django.db import migrations, models
import django.db.models.deletion


def create_default_hourSlotsGroup(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    HourSlotsGroup = apps.get_model("timetable", "HourSlotsGroup")
    School = apps.get_model("timetable", "School")
    SchoolYear = apps.get_model("timetable", "SchoolYear")
    school = School.objects.first()
    school_year = SchoolYear.objects.first()
    if school is not None and school_year is not None:
        # When we are creating the db in the first place, we do not have any element in it so .first() returns None.
        HourSlotsGroup.objects.using(db_alias).create(name="Default",
                                                      school=school,
                                                      school_year=school_year)


def remove_default_hourSlotsGroup(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    HourSlotsGroup = apps.get_model("timetable", "HourSlotsGroup")
    HourSlotsGroup.objects.using(db_alias).filter(name="Default").delete()
    HourSlotsGroup.objects.filter(name='Default HourSlotGroup').delete()


def create_hourSlotsGroup_per_school_and_school_year(apps, schema_editor):
    """
    Create a default hourslotgroup, one for each School and SchoolYear.
    """
    db_alias = schema_editor.connection.alias
    HourSlotsGroup = apps.get_model("timetable", "HourSlotsGroup")
    School = apps.get_model("timetable", "School")
    SchoolYear = apps.get_model("timetable", "SchoolYear")
    HourSlot = apps.get_model("timetable", "HourSlot")
    Course = apps.get_model("timetable", "Course")
    schools_and_school_years = HourSlot.objects.all().values('school', 'school_year').distinct()\
        .union(Course.objects.all().values('school', 'school_year').distinct())

    for hs in schools_and_school_years:
        # Create an HourSlotGroup for every school and school year (for which at least an HourSlot or Course exists)
        HourSlotsGroup.objects.using(db_alias).create(name="Default HourSlotGroup",
                                                      school=School.objects.get(id=hs['school']),
                                                      school_year=SchoolYear.objects.get(id=hs['school_year']))

    # Now change the foreign key for both hour slots and courses
    for c in Course.objects.all():
        c.hour_slots_group = HourSlotsGroup.objects.get(name='Default HourSlotGroup',
                                                        school=c.school,
                                                        school_year=c.school_year)
        c.save()
    for h in HourSlot.objects.all():
        h.hour_slots_group = HourSlotsGroup.objects.get(name='Default HourSlotGroup',
                                                        school=h.school,
                                                        school_year=h.school_year)
        h.save()

    # Here we can safely delete the Default HourSlotsGroup (the one with id=1)
    HourSlotsGroup.objects.filter(name='Default').delete()



def remove_hourSlotsGroup_per_school_and_school_year(apps, schema_editor):
    """
    This should not be necessary. All HourSlotsGroups are deleted in the remove_default_hourSlotsGroup method.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0022_create_hourslotgroup_model'),
    ]
    operations = [
        migrations.RunPython(create_default_hourSlotsGroup, remove_default_hourSlotsGroup),
        migrations.AddField(
            model_name='course',
            name='hour_slots_group',
            # Here putting default = 1 is a bit of a bet for the hourslotgroup created in create_default_hourSlotGroup
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                                    to='timetable.HourSlotsGroup', verbose_name='hour slots group',
                                    null=False, blank=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hourslot',
            name='hour_slots_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                                    to='timetable.HourSlotsGroup', verbose_name='hour slots group'),
            preserve_default=False,
        ),
        migrations.RunPython(create_hourSlotsGroup_per_school_and_school_year,
                             remove_hourSlotsGroup_per_school_and_school_year)
    ]