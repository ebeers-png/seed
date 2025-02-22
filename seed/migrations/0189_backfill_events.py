# Generated by Django 3.2.17 on 2023-03-11 00:30

from django.db import migrations, transaction


@transaction.atomic
def backfill_at_events(apps, schema_editor):
    BuildingFile = apps.get_model("seed", "BuildingFile")
    PropertyView = apps.get_model("seed", "PropertyView")
    ATEvent = apps.get_model("seed", "ATEvent")
    Scenario = apps.get_model("seed", "Scenario")

    building_files = BuildingFile.objects.all()
    for building_file in building_files:
        if building_file.property_state is None:
            continue

        propertyview = PropertyView.objects.filter(state=building_file.property_state).first()
        if propertyview is None:
            continue

        event = ATEvent.objects.create(
            property=propertyview.property,
            cycle=propertyview.cycle,
            building_file=building_file,
            created=building_file.created,
            modified=building_file.created,
            audit_date=propertyview.state.extra_data.get('audit_date', '')
        )
        scenarios = Scenario.objects.filter(property_state=propertyview.state_id)
        for scenario in scenarios:
            scenario.event = event
            scenario.save()

        event.save()


@transaction.atomic
def backfill_analysis_events(apps, schema_editor):
    Analysis = apps.get_model("seed", "Analysis")
    AnalysisEvent = apps.get_model("seed", "AnalysisEvent")

    analysises = Analysis.objects.all()
    for analysis in analysises:
        for propertyview in analysis.analysispropertyview_set.all():
            AnalysisEvent.objects.create(
                property=propertyview.property,
                cycle=propertyview.cycle,
                analysis=analysis,
                created=analysis.created_at,
                modified=analysis.created_at,
            ).save()


@transaction.atomic
def backfill_note_events(apps, schema_editor):
    Note = apps.get_model("seed", "Note")
    NoteEvent = apps.get_model("seed", "NoteEvent")

    notes = Note.objects.filter(property_view__isnull=False)
    for note in notes:
        NoteEvent.objects.create(
            property=note.property_view.property,
            cycle=note.property_view.cycle,
            note=note,
            created=note.created,
            modified=note.created,
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0188_auto_20230217_1652'),
    ]

    operations = [
        migrations.RunPython(backfill_at_events),
        migrations.RunPython(backfill_analysis_events),
        migrations.RunPython(backfill_note_events),
    ]
