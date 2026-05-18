# Generated manually to convert Material text fields to ForeignKeys safely.

from django.db import migrations, models
import django.db.models.deletion


def make_unique_symbol(model, base_symbol):
    base_symbol = str(base_symbol or '').strip()[:10] or 'N/A'
    symbol = base_symbol
    counter = 1

    while model.objects.filter(symbol__iexact=symbol).exists():
        suffix = str(counter)
        symbol = f"{base_symbol[:10 - len(suffix)]}{suffix}"
        counter += 1

    return symbol


def forwards(apps, schema_editor):
    Material = apps.get_model('materials', 'Material')
    Unit = apps.get_model('materials', 'Unit')
    MaterialType = apps.get_model('materials', 'MaterialType')
    Status = apps.get_model('core', 'Status')

    for material in Material.objects.all():
        old_unit = str(getattr(material, 'unit', '') or '').strip()
        old_material_type = str(getattr(material, 'material_type', '') or '').strip()
        old_status = str(getattr(material, 'status', '') or '').strip()

        if old_unit:
            unit_obj = (
                Unit.objects.filter(symbol__iexact=old_unit).first()
                or Unit.objects.filter(name__iexact=old_unit).first()
            )

            if not unit_obj:
                unit_obj = Unit.objects.create(
                    name=old_unit,
                    symbol=make_unique_symbol(Unit, old_unit)
                )

            material.unit_fk = unit_obj

        if old_material_type:
            material_type_obj = (
                MaterialType.objects.filter(symbol__iexact=old_material_type).first()
                or MaterialType.objects.filter(name__iexact=old_material_type).first()
            )

            if not material_type_obj:
                material_type_obj = MaterialType.objects.create(
                    name=old_material_type,
                    symbol=make_unique_symbol(MaterialType, old_material_type)
                )

            material.material_type_fk = material_type_obj

        if old_status:
            status_obj = Status.objects.filter(name__iexact=old_status).first()

            if not status_obj:
                status_obj = Status.objects.create(
                    name=old_status,
                    is_active=True
                )

            material.status_fk = status_obj

        material.save()


def backwards(apps, schema_editor):
    Material = apps.get_model('materials', 'Material')

    for material in Material.objects.all():
        if material.unit_fk:
            material.unit = material.unit_fk.symbol or material.unit_fk.name

        if material.material_type_fk:
            material.material_type = material.material_type_fk.name

        if material.status_fk:
            material.status = material.status_fk.name

        material.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('materials', '0003_materialtype_unit_alter_material_id_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='unit_fk',
            field=models.ForeignKey(
                to='materials.unit',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='material_type_fk',
            field=models.ForeignKey(
                to='materials.materialtype',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='status_fk',
            field=models.ForeignKey(
                to='core.status',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name='material',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='material',
            name='material_type',
        ),
        migrations.RemoveField(
            model_name='material',
            name='status',
        ),
        migrations.RenameField(
            model_name='material',
            old_name='unit_fk',
            new_name='unit',
        ),
        migrations.RenameField(
            model_name='material',
            old_name='material_type_fk',
            new_name='material_type',
        ),
        migrations.RenameField(
            model_name='material',
            old_name='status_fk',
            new_name='status',
        ),
    ]