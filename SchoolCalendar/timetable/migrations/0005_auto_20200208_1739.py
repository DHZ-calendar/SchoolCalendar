# Generated by Django 3.0.3 on 2020-02-08 17:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0004_auto_20200208_1722'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stage',
            old_name='date',
            new_name='date_end',
        ),
        migrations.AddField(
            model_name='stage',
            name='date_start',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
