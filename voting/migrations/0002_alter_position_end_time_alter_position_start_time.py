# Generated by Django 5.2.3 on 2025-06-28 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='Legacy field - voting times are now set globally in Election Settings', null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='Legacy field - voting times are now set globally in Election Settings', null=True),
        ),
    ]
