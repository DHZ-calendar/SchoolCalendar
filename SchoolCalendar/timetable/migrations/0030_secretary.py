# Generated by Django 3.2.6 on 2021-09-06 13:18

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0029_assignment_substituted_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Secretary',
            fields=[
                ('myuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='timetable.myuser')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.school', verbose_name='school')),
            ],
            options={
                'verbose_name': 'Secretary',
            },
            bases=('timetable.myuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]