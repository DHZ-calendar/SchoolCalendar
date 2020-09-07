# Generated by Django 3.0.8 on 2020-09-06 09:55

from django.db import migrations, models
import django.db.models.deletion


def create_default_hourSlotsGroup(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    HourSlotsGroup = apps.get_model("timetable", "HourSlotsGroup")
    School = apps.get_model("timetable", "School")
    SchoolYear = apps.get_model("timetable", "SchoolYear")
    school = School.objects.first()
    school_year = SchoolYear.objects.first()
    HourSlotsGroup.objects.using(db_alias).create(name="Default",
                                                  school=school,
                                                  school_year=school_year)


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0020_auto_20200720_2254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='school',
        ),
        migrations.RemoveField(
            model_name='course',
            name='school_year',
        ),
        migrations.RemoveField(
            model_name='hourslot',
            name='school',
        ),
        migrations.RemoveField(
            model_name='hourslot',
            name='school_year',
        ),
        migrations.CreateModel(
            name='HourSlotsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.School', verbose_name='school')),
                ('school_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='timetable.SchoolYear', verbose_name='school year')),
            ],
        ),
        migrations.RunPython(create_default_hourSlotsGroup),
        migrations.AddField(
            model_name='course',
            name='hour_slots_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='timetable.HourSlotsGroup', verbose_name='hour slots group'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hourslot',
            name='hour_slots_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='timetable.HourSlotsGroup', verbose_name='hour slots group'),
            preserve_default=False,
        ),
    ]