from django.db import models
from django.contrib.auth.models import User


class Application(models.Model):
    name = models.CharField(max_length=200, unique=True)
    company = models.CharField(max_length=200, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.company:
            return '{0} by {1}'.format(self.name, self.company)
        return self.name

CRASH_KIND_CHOICES = tuple(enumerate((
    'Annoyance',
    'Crash',
    'Hang',
    'Severe Data Loss',
)))

CRASH_KIND = dict((n.lower(), i) for (i, n) in CRASH_KIND_CHOICES)

class CrashReport(models.Model):
    application = models.ForeignKey(Application, related_name='crash_reports')
    version = models.CharField(max_length=25, blank=True)
    kind = models.IntegerField(choices=CRASH_KIND_CHOICES, db_index=True, default=0)
    user = models.ForeignKey(User, related_name='crash_reports')
    details = models.TextField(blank=True)
    title = models.CharField(max_length=200, db_index=True)
    count = models.IntegerField(default=1)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{title} ({app} {type} by {user})'.format(
            title=self.title,
            app=self.application.name,
            type=self.get_kind_display().lower(),
            user=self.user.username,
        )

