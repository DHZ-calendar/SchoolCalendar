# Generated by Django 3.0.8 on 2020-07-20 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0018_auto_20200720_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachersyearlyload',
            name='yearly_load_co_teaching',
            field=models.IntegerField(default=0, verbose_name='yearly load co-teaching'),
        ),
    ]
