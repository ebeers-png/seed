# Generated by Django 3.2.13 on 2022-05-11 18:29

from django.db import migrations, models, transaction
import django.db.models.deletion

def forwards(apps, schema_editor):
    DerivedColumn = apps.get_model("seed", "DerivedColumn")
    Column = apps.get_model("seed", "Column")

    with transaction.atomic():
        Column.objects.all().update(derived_column=None)
        for col in Column.objects.all():
            if not col.display_name:
                col.display_name = col.column_description
                col.save()
        for dc in DerivedColumn.objects.all():
            # Generate a related column for each existing derived column
            Column.objects.create(
                derived_column=dc,
                column_name=dc.name,
                display_name=dc.name,
                column_description=dc.name,
                table_name=dc.inventory_type,
                organization=dc.organization
            )


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0169_auto_20220616_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='derived_column',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seed.derivedcolumn'),
        ),
        migrations.RunPython(forwards),
    ]
