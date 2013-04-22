from django import forms

from crashes.models import CRASH_KIND, Application
from crashes.forms import *
from crashes.tests.helpers import *


def test_crash_form_has_version():
    field = form_field(CrashForm, 'version')
    assert isinstance(field, forms.CharField)
    assert field.max_length == 25

def test_crash_form_has_details():
    field = form_field(CrashForm, 'details')
    assert isinstance(field, forms.CharField)
    assert isinstance(field.widget, forms.Textarea)
    assert not field.required

def test_crash_form_has_title():
    field = form_field(CrashForm, 'title')
    assert isinstance(field, forms.CharField)
    assert field.max_length == 200

def test_crash_form_has_kind():
    field = form_field(CrashForm, 'kind')
    assert isinstance(field, forms.IntegerField)

def test_crash_form_has_application_field(db):
    field = form_field(CrashForm, 'application')
    assert isinstance(field, forms.ModelChoiceField)
    assert str(field.queryset.query) == str(Application.objects.all().query)

def test_crash_form_has_count_field():
    field = form_field(CrashForm, 'count')
    assert isinstance(field, forms.IntegerField)
    assert field.min_value == 1

