from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0021_remove_const_not_null'),
    ]
    operations = [
        migrations.CreateModel(
            name='HourSlotsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.School',
                                             verbose_name='school')),
                ('school_year',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='timetable.SchoolYear',
                                   verbose_name='school year')),
            ],
        )
    ]