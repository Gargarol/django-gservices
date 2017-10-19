from django import forms
from .models import TestFileUploadModel


class TestFileUploadForm(forms.ModelForm):
    class Meta:
        model = TestFileUploadModel
        exclude = []
