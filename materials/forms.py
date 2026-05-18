from django import forms
from .models import Material


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'id_material',
            'name',
            'description',
            'unit',
            'material_type',
            'status',
        ]

        widgets = {
            'unit': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
            }),
            'material_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
            }),
        }

    def clean_id_material(self):
        id_material = self.cleaned_data.get('id_material')

        if not id_material:
            raise forms.ValidationError('Material ID is required.')

        id_material = id_material.strip()

        if len(id_material) < 3:
            raise forms.ValidationError('Material ID must have at least 3 characters.')

        exists = Material.objects.filter(id_material__iexact=id_material)

        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise forms.ValidationError('This Material ID already exists.')

        return id_material

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError('Name is required.')

        name = name.strip()

        if len(name) < 2:
            raise forms.ValidationError('Name must have at least 2 characters.')

        return name

    def clean_unit(self):
        unit = self.cleaned_data.get('unit')

        if not unit:
            raise forms.ValidationError('Unit is required.')

        return unit

    def clean_material_type(self):
        material_type = self.cleaned_data.get('material_type')

        if not material_type:
            raise forms.ValidationError('Material type is required.')

        return material_type

    def clean_status(self):
        status = self.cleaned_data.get('status')

        if not status:
            raise forms.ValidationError('Status is required.')

        return status


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Material CSV File',
        help_text='The file must contain headers that match the material fields.',
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#233b6e]'
        })
    )