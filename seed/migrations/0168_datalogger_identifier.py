# Generated by Django 3.2.13 on 2022-06-09 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0167_auto_20220608_0759'),
    ]

    operations = [
        migrations.AddField(
            model_name='datalogger',
            name='identifier',
            field=models.CharField(default='', max_length=255),
        ),
    ]
