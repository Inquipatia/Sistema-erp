import csv
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse
from django.contrib import messages

from core.models import Status
from users.models import UserRole
from .models import Material, Unit, MaterialType
from .forms import MaterialForm, CsvUploadForm


def get_materials_permission(user):
    return (
        UserRole.objects.filter(user=user).aggregate(
            max_permission=models.Max("role__materials")
        )["max_permission"]
        or 0
    )


@login_required
def materials_list(request):
    max_permission = get_materials_permission(request.user)

    if max_permission < 1:
        return redirect("dashboard")

    material_list = Material.objects.all().order_by("id")

    all_material_types = MaterialType.objects.all().order_by("name")
    all_statuses = Status.objects.all().order_by("name")

    id_material = request.GET.get("id_material")
    name = request.GET.get("name")
    material_type = request.GET.get("material_type")
    status = request.GET.get("status")

    if id_material:
        material_list = material_list.filter(id_material__icontains=id_material)

    if name:
        material_list = material_list.filter(name__icontains=name)

    if material_type:
        material_list = material_list.filter(material_type_id=material_type)

    if status:
        material_list = material_list.filter(status_id=status)

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="materials.csv"'

        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";")
        writer.writerow([
            "ID Material",
            "Name",
            "Description",
            "Unit",
            "Type",
            "Status",
            "Created By",
            "Created At",
            "Updated At",
        ])

        for material in material_list:
            writer.writerow([
                material.id_material or "",
                material.name or "",
                material.description or "",
                material.unit.symbol if material.unit else "",
                material.material_type.name if material.material_type else "",
                material.status.name if material.status else "",
                material.created_by.username if material.created_by else "N/A",
                material.created_at.strftime("%Y-%m-%d %H:%M:%S") if material.created_at else "",
                material.updated_at.strftime("%Y-%m-%d %H:%M:%S") if material.updated_at else "",
            ])

        return response

    paginator = Paginator(material_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "materials/materials_list.html",
        {
            "page_obj": page_obj,
            "max_permission": max_permission,
            "all_material_types": all_material_types,
            "all_statuses": all_statuses,
        },
    )


@login_required
def material_create(request):
    max_permission = get_materials_permission(request.user)

    if max_permission < 2:
        return redirect("materials:materials_list")

    if request.method == "POST":
        form = MaterialForm(request.POST)

        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()

            return redirect("materials:materials_list")
    else:
        form = MaterialForm()

    return render(
        request,
        "materials/materials_form.html",
        {
            "form": form,
            "title": "Create New Material",
        },
    )


@login_required
def material_edit(request, pk):
    max_permission = get_materials_permission(request.user)

    if max_permission < 2:
        return redirect("materials:materials_list")

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material)

        if form.is_valid():
            form.save()
            return redirect("materials:materials_list")
    else:
        form = MaterialForm(instance=material)

    return render(
        request,
        "materials/materials_form.html",
        {
            "form": form,
            "material": material,
            "title": "Edit Material",
        },
    )


@login_required
def material_delete(request, pk):
    max_permission = get_materials_permission(request.user)

    if max_permission < 2:
        return redirect("materials:materials_list")

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":
        material.delete()

    return redirect("materials:materials_list")


@login_required
def material_bulk_create(request):
    max_permission = get_materials_permission(request.user)

    if max_permission < 2:
        return redirect("materials:materials_list")

    if request.method == "POST":
        form = CsvUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            try:
                data_set = csv_file.read().decode("UTF-8")
            except UnicodeDecodeError:
                csv_file.seek(0)
                data_set = csv_file.read().decode("ISO-8859-1")

            io_string = io.StringIO(data_set)

            sample = data_set[:2048]

            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,")
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = ";"

            reader = csv.DictReader(io_string, delimiter=delimiter)

            if reader.fieldnames:
                if reader.fieldnames[0].startswith("\ufeff"):
                    reader.fieldnames[0] = reader.fieldnames[0].lstrip("\ufeff")

                reader.fieldnames = [
                    key.strip().lower()
                    for key in reader.fieldnames
                ]

            unit_map = {}

            for unit in Unit.objects.all():
                if unit.symbol:
                    unit_map[unit.symbol.strip().lower()] = unit

                if unit.name:
                    unit_map[unit.name.strip().lower()] = unit

            material_type_map = {}

            for material_type in MaterialType.objects.all():
                if material_type.symbol:
                    material_type_map[material_type.symbol.strip().lower()] = material_type

                if material_type.name:
                    material_type_map[material_type.name.strip().lower()] = material_type

            status_map = {}

            for status in Status.objects.all():
                if status.name:
                    status_map[status.name.strip().lower()] = status

            successful_records = []
            error_records = []
            materials_to_create = []
            seen_ids = set()

            for i, row in enumerate(reader):
                row_number = i + 2
                form_data = {}
                row_errors = {}

                for key, value in row.items():
                    if key is None:
                        continue

                    clean_key = key.strip().lower()
                    clean_value = value.strip() if isinstance(value, str) else value
                    form_data[clean_key] = clean_value

                id_material = form_data.get("id_material", "")
                unit_value = form_data.get("unit", "")
                material_type_value = form_data.get("material_type", "")
                status_value = form_data.get("status", "")

                if id_material:
                    id_material_lower = id_material.strip().lower()

                    if id_material_lower in seen_ids:
                        row_errors["id_material"] = "This Material ID is duplicated inside the uploaded file."
                    else:
                        seen_ids.add(id_material_lower)

                    if Material.objects.filter(id_material__iexact=id_material).exists():
                        row_errors["id_material"] = "This Material ID already exists in the database."
                else:
                    row_errors["id_material"] = "Material ID is required."

                if unit_value:
                    unit_obj = unit_map.get(unit_value.strip().lower())

                    if unit_obj:
                        form_data["unit"] = unit_obj.pk
                    else:
                        row_errors["unit"] = f'Unit "{unit_value}" not found or invalid.'
                else:
                    row_errors["unit"] = "Unit is required."

                if material_type_value:
                    material_type_obj = material_type_map.get(material_type_value.strip().lower())

                    if material_type_obj:
                        form_data["material_type"] = material_type_obj.pk
                    else:
                        row_errors["material_type"] = f'Material Type "{material_type_value}" not found or invalid.'
                else:
                    row_errors["material_type"] = "Material Type is required."

                if status_value:
                    status_obj = status_map.get(status_value.strip().lower())

                    if status_obj:
                        form_data["status"] = status_obj.pk
                    else:
                        row_errors["status"] = f'Status "{status_value}" not found or invalid.'
                else:
                    row_errors["status"] = "Status is required."

                material_form = MaterialForm(form_data)

                if material_form.is_valid() and not row_errors:
                    material = material_form.save(commit=False)
                    material.created_by = request.user
                    materials_to_create.append(material)

                    successful_records.append({
                        "row": row_number,
                        "data": form_data,
                    })
                else:
                    errors = {
                        field: ", ".join(err)
                        for field, err in material_form.errors.items()
                    }

                    errors.update(row_errors)

                    error_records.append({
                        "row": row_number,
                        "data": form_data,
                        "errors": errors,
                    })

            if materials_to_create:
                Material.objects.bulk_create(materials_to_create)

            messages.success(
                request,
                f"Process finished. {len(successful_records)} materials created successfully.",
            )

            context = {
                "form": form,
                "successful_count": len(successful_records),
                "error_count": len(error_records),
                "total_rows": len(successful_records) + len(error_records),
                "error_records": error_records,
                "successful_records": successful_records,
                "report_generated": True,
            }

            return render(request, "materials/materials_bulk_upload.html", context)

    else:
        form = CsvUploadForm()

    return render(request, "materials/materials_bulk_upload.html", {"form": form})


@login_required
def download_template_materials(request):
    header_fields = [
        "id_material",
        "name",
        "description",
        "unit",
        "material_type",
        "status",
    ]

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="material_template.csv"'

    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(header_fields)

    return response