# Generated by Django 5.1.6 on 2025-02-09 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HealthStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_percent', models.FloatField()),
                ('total_cores', models.IntegerField()),
                ('every_cpu_core_percent', models.JSONField()),
                ('ram_percent', models.FloatField()),
                ('ssd_usage', models.FloatField()),
            ],
        ),
    ]
