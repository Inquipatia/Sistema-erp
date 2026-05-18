import csv
import re
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse

from users.models import UserRole
from .models import Supplier
from .forms import SupplierForm, CsvUploadForm
from django.contrib import messages


def get_suppliers_permission(user):
    return UserRole.objects.filter(
        user=user
    ).aggregate(
        max_permission=models.Max('role__suppliers')
    )['max_permission'] or 0


@login_required
def suppliers_list(request):
    max_permission = get_suppliers_permission(request.user)

    if max_permission < 1:
        return redirect('dashboard')

    supplier_list = Supplier.objects.all().order_by('id')

    id_supplier = request.GET.get('id_supplier')
    name = request.GET.get('name')
    country = request.GET.get('country')
    status = request.GET.get('status')

    if id_supplier:
        supplier_list = supplier_list.filter(id_supplier__icontains=id_supplier)

    if name:
        supplier_list = supplier_list.filter(name__icontains=name)

    if country:
        supplier_list = supplier_list.filter(country__icontains=country)

    if status:
        supplier_list = supplier_list.filter(status=status)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'

        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'ID Supplier',
            'Legal Name',
            'Name',
            'Tax ID',
            'Country',
            'State/Province',
            'City',
            'Address',
            'Zip Code',
            'Phone',
            'Email',
            'Contact Name',
            'Contact Role',
            'Category',
            'Payment Terms',
            'Currency',
            'Payment Method',
            'Bank Account',
            'Status',
            'Created By',
            'Created At',
            'Updated At',
        ])

        for supplier in supplier_list:
            writer.writerow([
                supplier.id_supplier or '',
                supplier.legal_name or '',
                supplier.name or '',
                supplier.tax_id or '',
                supplier.country or '',
                supplier.state_province or '',
                supplier.city or '',
                supplier.address or '',
                supplier.zip_code or '',
                supplier.phone or '',
                supplier.email or '',
                supplier.contact_name or '',
                supplier.contact_role or '',
                supplier.category or '',
                supplier.payment_terms or '',
                supplier.currency or '',
                supplier.payment_method or '',
                supplier.bank_account or '',
                supplier.status or '',
                supplier.created_by.username if supplier.created_by else 'N/A',
                supplier.created_at.strftime('%Y-%m-%d %H:%M:%S') if supplier.created_at else '',
                supplier.updated_at.strftime('%Y-%m-%d %H:%M:%S') if supplier.updated_at else '',
            ])

        return response

    paginator = Paginator(supplier_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'suppliers/suppliers_list.html', {
        'page_obj': page_obj,
        'max_permission': max_permission,
    })


@login_required
def supplier_create(request):
    max_permission = get_suppliers_permission(request.user)

    if max_permission < 2:
        return redirect('suppliers:suppliers_list')

    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()

            return redirect('suppliers:suppliers_list')
    else:
        form = SupplierForm()

    return render(request, 'suppliers/suppliers_form.html', {
        'form': form,
        'title': 'Create New Supplier',
    })


@login_required
def supplier_edit(request, pk):
    max_permission = get_suppliers_permission(request.user)

    if max_permission < 2:
        return redirect('suppliers:suppliers_list')

    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            form.save()
            return redirect('suppliers:suppliers_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'suppliers/suppliers_form.html', {
        'form': form,
        'supplier': supplier,
        'title': 'Edit Supplier',
    })


@login_required
def supplier_delete(request, pk):
    max_permission = get_suppliers_permission(request.user)

    if max_permission < 2:
        return redirect('suppliers:suppliers_list')

    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()

    return redirect('suppliers:suppliers_list')


@login_required
def supplier_bulk_create(request):
    max_permission = get_suppliers_permission(request.user)

    if max_permission < 2:
        return redirect('suppliers:suppliers_list')

    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                data_set = csv_file.read().decode('UTF-8')
            except UnicodeDecodeError:
                csv_file.seek(0)
                data_set = csv_file.read().decode('ISO-8859-1')

            io_string = io.StringIO(data_set)

            # Detecta si el CSV viene separado por ; o por ,
            sample = data_set[:2048]
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=';,')
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = ';'

            reader = csv.DictReader(io_string, delimiter=delimiter)

            if reader.fieldnames:
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].lstrip('\ufeff')

                reader.fieldnames = [
                    key.strip().lower()
                    for key in reader.fieldnames
                ]

            successful_records = []
            error_records = []
            suppliers_to_create = []
            seen_ids = set()
            seen_emails = set()

            for i, row in enumerate(reader):
                row_number = i + 2
                form_data = {}

                for key, value in row.items():
                    if key is None:
                        continue

                    clean_key = key.strip().lower()

                    if isinstance(value, str):
                        clean_value = value.strip()
                    else:
                        clean_value = value

                    form_data[clean_key] = clean_value

                id_supplier = form_data.get('id_supplier', '')
                email = form_data.get('email', '')

                row_errors = {}

                if id_supplier:
                    id_supplier_lower = id_supplier.lower()

                    if id_supplier_lower in seen_ids:
                        row_errors['id_supplier'] = 'This Supplier ID is duplicated inside the uploaded file.'
                    else:
                        seen_ids.add(id_supplier_lower)

                if email:
                    email_lower = email.lower()

                    if email_lower in seen_emails:
                        row_errors['email'] = 'This Email is duplicated inside the uploaded file.'
                    else:
                        seen_emails.add(email_lower)

                supplier_form = SupplierForm(form_data)

                if supplier_form.is_valid() and not row_errors:
                    supplier = supplier_form.save(commit=False)
                    supplier.created_by = request.user
                    suppliers_to_create.append(supplier)

                    successful_records.append({
                        'row': row_number,
                        'data': form_data
                    })
                else:
                    errors = {
                        field: ', '.join(err)
                        for field, err in supplier_form.errors.items()
                    }

                    errors.update(row_errors)

                    error_records.append({
                        'row': row_number,
                        'data': form_data,
                        'errors': errors
                    })

            if suppliers_to_create:
                Supplier.objects.bulk_create(suppliers_to_create)

            messages.success(
                request,
                f'Process finished. {len(successful_records)} suppliers created successfully.'
            )

            context = {
                'form': form,
                'successful_count': len(successful_records),
                'error_count': len(error_records),
                'total_rows': len(successful_records) + len(error_records),
                'error_records': error_records,
                'successful_records': successful_records,
                'report_generated': True,
            }

            return render(request, 'suppliers/suppliers_bulk_upload.html', context)

    else:
        form = CsvUploadForm()

    return render(request, 'suppliers/suppliers_bulk_upload.html', {
        'form': form
    })
            

@login_required
def download_template_suppliers(request):
    header_fields = [
        'id_supplier',
        'legal_name',
        'name',
        'tax_id',
        'country',
        'state_province',
        'city',
        'address',
        'zip_code',
        'phone',
        'email',
        'contact_name',
        'contact_role',
        'category',
        'payment_terms',
        'currency',
        'payment_method',
        'bank_account',
        'status',
    ]

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="supplier_template.csv"'

    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(header_fields)

    return response