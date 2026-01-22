from django import forms

class DocumentUploadForm(forms.Form):
    original_name = forms.CharField(
        max_length=255,
        label="Nombre del documento",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    file = forms.FileField(
        label="Archivo",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
