# Generated by Django 3.2.12 on 2022-04-11 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0160_merge_0159_auto_20220310_1648_0159_inventorydocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorydocument',
            name='file_type',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'PDF'), (2, 'OSM'), (3, 'IDF'), (4, 'DXF')], default=0),
        ),
    ]
