from django import forms
from .models import Customer


INPUT_CLASS = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]"


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
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

        widgets = {
            "country": forms.Select(attrs={"class": INPUT_CLASS}),
            "currency": forms.Select(attrs={"class": INPUT_CLASS}),
            "status": forms.Select(attrs={"class": INPUT_CLASS}),
        }

    def clean_id_customer(self):
        id_customer = self.cleaned_data.get("id_customer")

        if not id_customer:
            raise forms.ValidationError("Customer ID is required.")

        id_customer = id_customer.strip()

        exists = Customer.objects.filter(id_customer__iexact=id_customer)

        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise forms.ValidationError("This Customer ID already exists.")

        return id_customer

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get("zip_code")

        if zip_code and not str(zip_code).isdigit():
            raise forms.ValidationError("Zip Code must contain only numbers.")

        return zip_code

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError("Email is required.")

        email = email.strip().lower()

        exists = Customer.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise forms.ValidationError("This email already exists.")

        return email


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Customer CSV File",
        help_text="The file must contain headers that match the customer fields.",
        widget=forms.ClearableFileInput(attrs={
            "class": INPUT_CLASS
        })
    )