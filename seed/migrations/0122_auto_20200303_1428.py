# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2020-03-03 22:28
from __future__ import unicode_literals

from django.db import migrations, models


def set_conversion_factor(apps, schema_editor):
    """Set all meter readings conversion_factor to 1.0, for kBtu
    Checks that there are no meter readings where conversion_factor is null and the
    source_unit is not kbtu
    """
    db_alias = schema_editor.connection.alias

    MeterReading = apps.get_model('seed', 'MeterReading')
    readings = MeterReading.objects.using(db_alias).filter(conversion_factor=None)
    bad_readings = []
    for reading in readings:
        reading_unit = reading.source_unit.lower().strip()
        if reading_unit != 'kbtu' and reading_unit != 'kbtu (thousand btu)':
            bad_readings.append({
                'meter': reading.meter.id,
                'source_unit': reading.source_unit,
                'start_time': reading.start_time,
                'end_time': reading.end_time})

    if bad_readings:
        raise Exception(f'Unexpected meter reading(s): conversion_factor is None and source_unit is not kbtu; {bad_readings}')

    readings.update(conversion_factor=1.0)


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0121_update_updated_timestamps'),
    ]

    operations = [
        migrations.RunPython(set_conversion_factor),
        migrations.AlterField(
            model_name='meterreading',
            name='conversion_factor',
            field=models.FloatField(),
        ),
    ]
