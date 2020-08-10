# Generated by Django 3.0.8 on 2020-08-09 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slowfit', '0002_auto_20200804_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='armLength',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='arm length in cm'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='dateOfBirth',
            field=models.DateField(blank=True, null=True, verbose_name='date of birth'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='height',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='height in cm'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='inseam',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='inseam in cm'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phoneAlt',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='alternative phone number'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='crankLength',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(165, '165mm'), (167.5, '167.5mm'), (170, '170mm'), (172.5, '172.5mm'), (175, '175mm')], null=True, verbose_name='current crank length'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='currentBike',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='slowfit.FrameSize', verbose_name='current bike'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='customerConcerns',
            field=models.TextField(blank=True, null=True, verbose_name="rider's specific concerns"),
        ),
        migrations.AlterField(
            model_name='visit',
            name='experience',
            field=models.TextField(blank=True, null=True, verbose_name='cycling experience'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='fitterConcerns',
            field=models.TextField(blank=True, null=True, verbose_name="fitter's concerns"),
        ),
        migrations.AlterField(
            model_name='visit',
            name='goals',
            field=models.TextField(blank=True, null=True, verbose_name='athletic goals'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='hx',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='current handlebar reach (mm)'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='hy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='current handlebar stack (mm)'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='injuries',
            field=models.TextField(blank=True, null=True, verbose_name='injuries and limitations'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='pedalSystem',
            field=models.TextField(blank=True, choices=[('Shimano', 'Shimano'), ('Look', 'Look'), ('Time', 'Time'), ('Speedplay', 'Speedplay')], null=True, verbose_name='pedal system'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='purpose',
            field=models.CharField(max_length=100, verbose_name='purpose of visit'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='saddle',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='current saddle'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='saddleBarDrop',
            field=models.SmallIntegerField(blank=True, help_text='positive: saddle higher than bar, negative: bar higher than saddle', null=True, verbose_name='current saddle to bar drop'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='saddleHeight',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='current saddle height'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='saddleSetback',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='current saddle setback/offset'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='sx',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='current saddle X'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='sy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='current saddle Y'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='weight',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='weight in kg'),
        ),
    ]