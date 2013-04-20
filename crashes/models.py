from django.db import models
from django.contrib.auth.models import User


class Application(models.Model):
    name = models.CharField(max_length=200, unique=True)
    company = models.CharField(max_length=200, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'name=%r, company=%r' % (
            self.name,
            self.company,
        )

CRASH_KIND_CHOICES = tuple(enumerate((
    'Annoyance',
    'Crash',
    'Hang',
    'Data Loss',
)))

CRASH_KIND = dict((n.lower(), i) for (i, n) in CRASH_KIND_CHOICES)

class CrashReport(models.Model):
    application = models.ForeignKey(Application, related_name='crash_reports')
    version = models.CharField(max_length=25, blank=True)
    kind = models.IntegerField(choices=CRASH_KIND_CHOICES, db_index=True, default=0)
    user = models.ForeignKey(User, related_name='crash_reports')
    details = models.TextField(blank=True)
    title = models.CharField(max_length=200, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'version=%r, user=%r, title=%r, count=%r' % (
            self.version,
            self.user,
            self.title,
            self.count,
        )

    @property
    def count(self):
        return self.crashes.count()

class Crash(models.Model):
    crash_report = models.ForeignKey(CrashReport, related_name='crashes')
    user = models.ForeignKey(User, related_name='crashes')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'crash_report=%r updated_at=%r' % (
            self.crash_report,
            self.updated_at,
        )

