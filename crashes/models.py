from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'name=%r' % self.name


class Application(models.Model):
    name = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(Company, null=True, blank=True, related_name='applications')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'name=%r, company=%r' % (
            self.name,
            self.company,
        )


class Version(models.Model):
    application = models.ForeignKey(Application, related_name='versions')
    marketing = models.CharField(max_length=20)
    build = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['application', 'build']

    def __unicode__(self):
        return 'app=%r, marketing=%r, build=%r' % (
            self.application,
            self.marketing,
            self.build,
        )


class CrashReport(models.Model):
    version = models.ForeignKey(Version, related_name='versions')
    user = models.ForeignKey(User, related_name='crash_reports')
    details = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    count = models.IntegerField(default=1)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'version', 'title']

    def __unicode__(self):
        return 'version=%r, user=%r, title=%r, count=%r' % (
            self.version,
            self.user,
            self.title,
            self.count,
        )

