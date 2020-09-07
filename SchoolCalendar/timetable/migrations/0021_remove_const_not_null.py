from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0020_auto_20200720_2254'),
    ]
    operations = [
        migrations.AlterField(
            model_name='course',
            name='school_year',
            field=models.ForeignKey(on_delete=models.deletion.PROTECT, to='timetable.SchoolYear', null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='course',
            name='school',
            field=models.ForeignKey(on_delete=models.deletion.PROTECT, to='timetable.School', null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='hourslot',
            name='school',
            field=models.ForeignKey(on_delete=models.deletion.PROTECT, to='timetable.School', null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='hourslot',
            name='school_year',
            field=models.ForeignKey(on_delete=models.deletion.PROTECT, to='timetable.SchoolYear', null=True, blank=True)
        ),





    ]