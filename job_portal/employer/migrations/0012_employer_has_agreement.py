# Generated by Django 5.1.4 on 2025-02-07 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0011_alter_jobpost_location_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='has_agreement',
            field=models.BooleanField(default=False, verbose_name='Sutartis'),
        ),
    ]
