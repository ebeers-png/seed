# Generated by Django 3.2.13 on 2022-06-28 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0169_auto_20220616_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertystate',
            name='at_building_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='taxlotstate',
            name='at_building_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
