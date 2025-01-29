# Generated by Django 5.1.4 on 2025-01-28 10:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_cv_attachment_cv_characteristics_cv_civil_status_and_more'),
        ('employer', '0004_jobagreement_job_post_jobagreement_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobagreement',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='agreements', to='employee.employee'),
        ),
    ]
