# Generated by Django 5.1.4 on 2025-02-04 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0009_alter_jobpost_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobpost',
            name='submitted_cvs',
        ),
    ]
