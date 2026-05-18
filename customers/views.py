import csv
import re
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse

from users.models import UserRole
from .models import Customer
from .forms import CustomerForm, CsvUploadForm
from django.contrib import messages


def get_customers_permission(user):
    return UserRole.objects.filter(
        user=user
    ).aggregate(
        max_permission=models.Max('role__customers')
    )['max_permission'] or 0


@login_required
def customers_list(request):
    max_permission = get_customers_permission(request.user)

    if max_permission < 1:
        return redirect('dashboard')

    customer_list = Customer.objects.all().order_by('id')

    id_customer = request.GET.get('id_customer')
    name = request.GET.get('name')
    country = request.GET.get('country')
    status = request.GET.get('status')

    if id_customer:
        customer_list = customer_list.filter(id_customer__icontains=id_customer)

    if name:
        customer_list = customer_list.filter(name__icontains=name)

    if country:
        customer_list = customer_list.filter(country__icontains=country)

    if status:
        customer_list = customer_list.filter(status=status)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'

        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'ID customer',
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

        for customer in customer_list:
            writer.writerow([
                customer.id_customer or '',
                customer.legal_name or '',
                customer.name or '',
                customer.tax_id or '',
                customer.country or '',
                customer.state_province or '',
                customer.city or '',
                customer.address or '',
                customer.zip_code or '',
                customer.phone or '',
                customer.email or '',
                customer.contact_name or '',
                customer.contact_role or '',
                customer.category or '',
                customer.payment_terms or '',
                customer.currency or '',
                customer.payment_method or '',
                customer.bank_account or '',
                customer.status or '',
                customer.created_by.username if customer.created_by else 'N/A',
                customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else '',
                customer.updated_at.strftime('%Y-%m-%d %H:%M:%S') if customer.updated_at else '',
            ])

        return response

    paginator = Paginator(customer_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customers/customers_list.html', {
        'page_obj': page_obj,
        'max_permission': max_permission,
    })


@login_required
def customer_create(request):
    max_permission = get_customers_permission(request.user)

    if max_permission < 2:
        return redirect('customers:customers_list')

    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()

            return redirect('customers:customers_list')
    else:
        form = CustomerForm()

    return render(request, 'customers/customers_form.html', {
        'form': form,
        'title': 'Create New customer',
    })


@login_required
def customer_edit(request, pk):
    max_permission = get_customers_permission(request.user)

    if max_permission < 2:
        return redirect('customers:customers_list')

    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            return redirect('customers:customers_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/customers_form.html', {
        'form': form,
        'customer': customer,
        'title': 'Edit customer',
    })


@login_required
def customer_delete(request, pk):
    max_permission = get_customers_permission(request.user)

    if max_permission < 2:
        return redirect('customers:customers_list')

    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()

    return redirect('customers:customers_list')


@login_required
def customer_bulk_create(request):
    max_permission = get_customers_permission(request.user)

    if max_permission < 2:
        return redirect('customers:customers_list')

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
            customers_to_create = []
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

                id_customer = form_data.get('id_customer', '')
                email = form_data.get('email', '')

                row_errors = {}

                if id_customer:
                    id_customer_lower = id_customer.lower()

                    if id_customer_lower in seen_ids:
                        row_errors['id_customer'] = 'This customer ID is duplicated inside the uploaded file.'
                    else:
                        seen_ids.add(id_customer_lower)

                if email:
                    email_lower = email.lower()

                    if email_lower in seen_emails:
                        row_errors['email'] = 'This Email is duplicated inside the uploaded file.'
                    else:
                        seen_emails.add(email_lower)

                customer_form = CustomerForm(form_data)

                if customer_form.is_valid() and not row_errors:
                    customer = customer_form.save(commit=False)
                    customer.created_by = request.user
                    customers_to_create.append(customer)

                    successful_records.append({
                        'row': row_number,
                        'data': form_data
                    })
                else:
                    errors = {
                        field: ', '.join(err)
                        for field, err in customer_form.errors.items()
                    }

                    errors.update(row_errors)

                    error_records.append({
                        'row': row_number,
                        'data': form_data,
                        'errors': errors
                    })

            if customers_to_create:
                Customer.objects.bulk_create(customers_to_create)

            messages.success(
                request,
                f'Process finished. {len(successful_records)} customers created successfully.'
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

            return render(request, 'customers/customers_bulk_upload.html', context)

    else:
        form = CsvUploadForm()

    return render(request, 'customers/customers_bulk_upload.html', {
        'form': form
    })
            

@login_required
def download_template_customers(request):
    header_fields = [
        "id_customer",
        "legal_name",
        "name",
        "tax_id",
        "country",
        "state_province",
        "city",
        "address",
        "zip_code",
        "phone",
        "email",
        "contact_name",
        "contact_role",
        "category",
        "payment_terms",
        "currency",
        "payment_method",
        "bank_account",
        "status",
    ]

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="customer_template.csv"'

    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(header_fields)

    return response