# Generated by Django 3.2.13 on 2022-04-29 20:40

from django.db import migrations, models

def forwards(apps, schema_editor):
    Column = apps.get_model("seed", "Column")
    Organization = apps.get_model("orgs", "Organization")

    # Go through all the organizations
    for org in Organization.objects.all():
        columns = Column.objects.filter(organization_id=org.id)

            for col in columns:
                if col.display_name is None or col.display_name == "":
                    col.column_description = col.column_name
                else:
                    col.column_description = col.display_name
                col.save()

class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0161_alter_inventorydocument_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='column_description',
            field=models.TextField(blank=True, default=models.CharField(db_index=True, max_length=512), max_length=1000),
        ),
        migrations.RunPython(forwards)
    ]
