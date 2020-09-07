from django.db import migrations


def do_nothing(apps, schema_editor):
    pass


def restore_FK(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Course = apps.get_model("timetable", "Course")
    HourSlot = apps.get_model("timetable", "HourSlot")
    for c in Course.objects.all():
        c.school_year = c.hour_slots_group.school_year
        c.school = c.hour_slots_group.school
        c.save()
    for h in HourSlot.objects.all():
        h.school_year = h.hour_slots_group.school_year
        h.school = h.hour_slots_group.school
        h.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0023_add_hourslotgroup_fk'),
    ]
    operations = [
        migrations.RunPython(do_nothing, restore_FK),

        migrations.RemoveField(
            model_name='course',
            name='school_year'
        ),
        migrations.RemoveField(
            model_name='course',
            name='school'
        ),
        migrations.RemoveField(
            model_name='hourslot',
            name='school_year',
        ),
        migrations.RemoveField(
            model_name='hourslot',
            name='school',
        ),
    ]