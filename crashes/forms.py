from django import forms

from crashes.models import Application, CrashReport

class CrashForm(forms.ModelForm):
    class Meta:
        model = CrashReport
        fields = ('application', 'title', 'kind', 'details', 'version', 'count')

