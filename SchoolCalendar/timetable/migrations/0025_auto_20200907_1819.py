# Generated by Django 3.0.8 on 2020-09-07 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0024_remove_fk_field_hoursslot_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='school',
        ),
        migrations.RemoveField(
            model_name='hoursperteacherinclass',
            name='school',
        ),
        migrations.RemoveField(
            model_name='stage',
            name='school',
        ),
    ]
