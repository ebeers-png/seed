# Generated by Django 3.2.13 on 2022-05-09 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0163_add_bae_assets_to_buildingsync_default_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='derivedcolumnparameter',
            name='source_column_derived',
            field=models.BooleanField(default=False),
        ),
    ]
