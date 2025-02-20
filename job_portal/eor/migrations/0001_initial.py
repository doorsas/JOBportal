# Generated by Django 5.1.4 on 2025-02-20 09:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0004_alter_customuser_groups_and_more'),
        ('employer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed')], default='active', max_length=50)),
                ('employer_payment', models.DecimalField(blank=True, decimal_places=2, help_text='Amount employer pays for the assignment', max_digits=10, null=True)),
                ('employee_salary', models.DecimalField(blank=True, decimal_places=2, help_text='Amount paid to the employee', max_digits=10, null=True)),
                ('manager_commission', models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Commission earned by the manager', max_digits=10, null=True)),
                ('cv', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.cv')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employer.employer')),
                ('job_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employer.jobpost')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_name', models.CharField(max_length=255)),
                ('manager_surname', models.CharField(max_length=255)),
                ('work_start_date', models.DateField(auto_now_add=True)),
                ('work_end_date', models.DateField(blank=True, null=True)),
                ('document', models.FileField(blank=True, null=True, upload_to='manager_agreements_documents/', verbose_name='manager_document')),
                ('employee_bonus_percentage', models.FloatField(default=50.0, help_text='Percentage of employer payment given to the employee')),
                ('employer_bonus_percentage', models.FloatField(default=20.0, help_text='Percentage of employer payment taken as profit')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
                ('employer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employer.employer')),
                ('manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Manager',
                'verbose_name_plural': 'Managers',
                'ordering': ['-work_start_date'],
            },
        ),
        migrations.CreateModel(
            name='DirectAgreements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(auto_now_add=True)),
                ('amount', models.FloatField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employer.employer')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eor.manager')),
            ],
            options={
                'verbose_name': 'Direct Agreement',
                'verbose_name_plural': 'Direct Agreements',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_tariff_type', models.CharField(choices=[('hourly', 'Už valandą'), ('daily', 'Už dieną')], default='hourly', max_length=10)),
                ('employee_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Darbuotojo valandinis tarifas', max_digits=10)),
                ('employee_daily_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Darbuotojo dienos tarifas', max_digits=10)),
                ('employer_tariff_type', models.CharField(choices=[('hourly', 'Už valandą'), ('daily', 'Už dieną')], default='hourly', max_length=10)),
                ('employer_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Darbdavio valandinis tarifas', max_digits=10)),
                ('employer_daily_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Darbdavio dienos tarifas', max_digits=10)),
                ('manager_commission', models.DecimalField(decimal_places=2, default=0.0, help_text='Menedžerio komisinių procentas', max_digits=5)),
                ('worked_hours', models.DecimalField(decimal_places=2, default=0.0, help_text='Faktiškai išdirbtos valandos', max_digits=6)),
                ('worked_days', models.DecimalField(decimal_places=2, default=0.0, help_text='Faktiškai išdirbtos dienos', max_digits=6)),
                ('business_hours', models.DecimalField(decimal_places=2, default=0.0, help_text='Faktiškai išdirbtos darbo valandos', max_digits=6)),
                ('business_days', models.DecimalField(decimal_places=2, default=0.0, help_text='Faktiškai išdirbtos darbo dienos', max_digits=6)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts_as_employee', to='employee.employee')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts_as_employer', to='employer.employer')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts_as_manager', to='eor.manager')),
            ],
        ),
    ]
