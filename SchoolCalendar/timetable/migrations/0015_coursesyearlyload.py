# Generated by Django 3.0.8 on 2020-07-16 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0014_teachersyearlyload'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursesYearlyLoad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yearly_load', models.IntegerField(verbose_name='yearly load')),
                ('yearly_load_bes', models.IntegerField(verbose_name='yearly load bes')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.Course', verbose_name='course')),
            ],
        ),
    ]
