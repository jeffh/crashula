import json

from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import (render_to_response, get_object_or_404, redirect)
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from crashes.models import CrashReport, Application
from crashes.forms import CrashForm


def _render(request, template, context=None):
    return render_to_response(template, context or {}, context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        return redirect('crashes_by_user', request.user.username)
    return _render(request, 'crashes/index.html')

@login_required
def new_crash(request, username):
    form = CrashForm()
    if request.method == 'POST':
        form = CrashForm(request.POST)
        if form.is_valid():
            crash_report, created = CrashReport.objects.get_or_create(
                application=Application.objects.all()[0],
                user=request.user,
                title=form.cleaned_data['title'],
                defaults=form.cleaned_data,
            )
            if not created:
                crash_report.count += 1
                crash_report.save()

            return redirect('crash_by_user', request.user.username, crash_report.id)
    return _render(request, 'crashes/new_crash.html', dict(form=form, page='new_crash'))

@login_required
def edit_crash(request, username, crash_report_id):
    crash_report = get_object_or_404(CrashReport, id=crash_report_id, user=request.user)
    form = CrashForm(instance=crash_report)
    if request.method == 'POST':
        form = CrashForm(request.POST)
        if form.is_valid():
            for name, value in form.cleaned_data.items():
                setattr(crash_report, name, value)
            crash_report.save()
            return redirect('crash_by_user', request.user.username, crash_report.id)
    return _render(request, 'crashes/new_crash.html', dict(
        form=form,
        crash_report=crash_report,
        page='edit_crash',
    ))

def crash_by_user(request, username, crash_report_id):
    user = get_object_or_404(User, username=username)
    crash_report = get_object_or_404(CrashReport, user=user, id=crash_report_id)
    return _render(request, 'crashes/user_crash.html', dict(
        crash_report=crash_report,
        page='crash_by_user',
    ))


def crashes_by_user(request, username):
    user = get_object_or_404(User, username=username)
    crash_reports = CrashReport.objects.filter(user=user)
    return _render(request, 'crashes/user_crashes.html', dict(
        crash_reports=crash_reports,
        page='crashes_by_user',
    ))

