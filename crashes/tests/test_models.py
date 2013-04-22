from django.db import models
from django.contrib.auth.models import User

from crashes.tests.helpers import *
from crashes import factories as f
from crashes.models import *
from crashes.tests.fixtures import *


def assert_date_fields(model_class):
    assert Fields(model_class).updated_at == DateTimeField(auto_now=True)
    assert Fields(model_class).created_at == DateTimeField(auto_now_add=True)

### APPLICATION

def test_application_fields():
    model = Fields(Application)
    assert model.name == CharField(max_length=200, unique=True)
    assert model.company == CharField(max_length=200, blank=True)
    assert_date_fields(Application)

def test_application_unicode(db):
    app = f.ApplicationFactory.build(name='foo', company='')
    assert unicode(app) == 'foo'

    app = f.ApplicationFactory.build(name='foo', company='bar')
    assert unicode(app) == 'foo by bar'

### CRASH REPORT

def test_crash_report_fields():
    model = Fields(CrashReport)
    assert model.application == ForeignKey(Application, related_name='crash_reports')
    assert model.version == CharField(max_length=25, blank=True)
    assert model.kind == IntegerField(choices=CRASH_KIND_CHOICES, db_index=True, default=0)
    assert model.user == ForeignKey(User, related_name='crash_reports')
    assert model.details == TextField(blank=True)
    assert model.title == CharField(max_length=200, db_index=True)
    assert model.count == IntegerField(default=1)
    assert_date_fields(CrashReport)

def test_crash_report_unicode(db):
    cr = f.CrashReportFactory.build(title='Foobar', user__username='Joe', application__name='xcode', kind=CRASH_KIND['crash'])
    assert unicode(cr) == 'Foobar (xcode crash by Joe)'

