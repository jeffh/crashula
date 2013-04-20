from django import forms

from crashes.models import Application

class CrashForm(forms.Form):
    application = forms.ModelChoiceField(Application.objects.all())
    title = forms.CharField(max_length=200)
    kind = forms.IntegerField()
    details = forms.CharField(widget=forms.Textarea, required=False)
    version = forms.CharField(max_length=25)

