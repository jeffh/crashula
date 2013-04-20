from django.db import models
from django.contrib.auth.models import User

from crashes.tests.helpers import *
from crashes.models import *


def assert_date_fields(model_class):
    assert Fields(model_class).updated_at == DateTimeField(auto_now=True)
    assert Fields(model_class).created_at == DateTimeField(auto_now_add=True)

### APPLICATION

def test_application_fields():
    model = Fields(Application)
    assert model.name == CharField(max_length=200, unique=True)
    assert model.company == CharField(max_length=200, blank=True)
    assert_date_fields(Application)

### CRASH REPORT

def test_crash_report_fields():
    model = Fields(CrashReport)
    assert model.application == ForeignKey(Application, related_name='crash_reports')
    assert model.version == CharField(max_length=25, blank=True)
    assert model.kind == IntegerField(choices=CRASH_KIND_CHOICES, db_index=True, default=0)
    assert model.user == ForeignKey(User, related_name='crash_reports')
    assert model.details == TextField(blank=True)
    assert model.title == CharField(max_length=200, db_index=True)
    assert_date_fields(CrashReport)

### CRASH

def test_crash_has_crash_report_field():
    model = Fields(Crash)
    assert model.crash_report == ForeignKey(CrashReport, related_name='crashes')
    assert model.user == ForeignKey(User, related_name='crashes')
    assert_date_fields(Crash)

