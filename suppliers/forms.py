import re
from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
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

        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
            }),
        }

    def clean_id_supplier(self):
        id_supplier = self.cleaned_data.get('id_supplier')

        if not id_supplier:
            raise forms.ValidationError('Supplier ID is required.')

        id_supplier = id_supplier.strip()

        if len(id_supplier) < 3:
            raise forms.ValidationError('Supplier ID must have at least 3 characters.')

        exists = Supplier.objects.filter(id_supplier__iexact=id_supplier)

        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise forms.ValidationError('This Supplier ID already exists.')

        return id_supplier

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError('Name is required.')

        name = name.strip()

        if len(name) < 2:
            raise forms.ValidationError('Name must have at least 2 characters.')

        return name

    def clean_tax_id(self):
        tax_id = self.cleaned_data.get('tax_id')

        if not tax_id:
            raise forms.ValidationError('Tax ID is required.')

        tax_id = tax_id.strip()

        if len(tax_id) < 6:
            raise forms.ValidationError('Tax ID must have at least 6 characters.')

        return tax_id

    def clean_country(self):
        country = self.cleaned_data.get('country')

        if not country:
            raise forms.ValidationError('Country is required.')

        return country.strip()

    def clean_city(self):
        city = self.cleaned_data.get('city')

        if not city:
            raise forms.ValidationError('City is required.')

        return city.strip()

    def clean_address(self):
        address = self.cleaned_data.get('address')

        if not address:
            raise forms.ValidationError('Address is required.')

        return address.strip()

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')

        if not zip_code:
            raise forms.ValidationError('Zip Code is required.')

        zip_code = str(zip_code).strip()

        if not zip_code.isdigit():
            raise forms.ValidationError('Zip Code must contain numbers only.')

        if len(zip_code) < 3 or len(zip_code) > 15:
            raise forms.ValidationError('Zip Code must be between 3 and 15 digits.')

        return zip_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            raise forms.ValidationError('Phone is required.')

        phone = str(phone).strip()

        if not re.match(r'^[0-9+\- ]{7,20}$', phone):
            raise forms.ValidationError(
                'Phone must contain between 7 and 20 characters. Only numbers, +, - and spaces are allowed.'
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError('Email is required.')

        return email.strip().lower()

    def clean_status(self):
        status = self.cleaned_data.get('status')

        if status not in ['Active', 'Inactive']:
            raise forms.ValidationError('Select a valid status.')

        return status


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Supplier CSV File',
        help_text='The file must contain headers that match the supplier fields.',
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
        })
    )