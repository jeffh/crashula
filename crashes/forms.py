from django import forms

class CrashReportForm(forms.Form):
    title = forms.CharField(max_length=200)
    details = forms.CharField(widget=forms.Textarea)
    count = forms.IntegerField(min_value=1)

