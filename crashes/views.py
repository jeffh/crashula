import json

from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import (render_to_response, get_object_or_404, redirect)
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from crashes.models import CrashReport, Version, Application
from crashes.forms import CrashReportForm


def _render(request, template, context=None):
    return render_to_response(template, context or {}, context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        return redirect('crashes_by_user', request.user.username)
    return _render(request, 'crashes/index.html')

@login_required
def versions(request):
    result = []
    for app in Application.objects.all().select_related():
        result.append(dict(
            name=app.name,
            company=app.company.name if app.company else None,
            versions=[dict(marketing=v.marketing, build=v.build)
                for v in app.versions.order_by('-build')]
        ))
    response = HttpResponse(json.dumps(result))
    response['Content-Type'] = 'application/json'
    return response

@login_required
def new_crash(request):
    form = CrashReportForm()
    if request.method == 'POST':
        form = CrashReportForm(request.POST)
        if form.is_valid():
            crash = CrashReport.objects.create(
                version=Version.objects.all()[0],
                user=request.user,
                **form.cleaned_data
            )
            return redirect('crash_by_user', request.user.username, crash.id)
    return _render(request, 'crashes/new_crash.html', dict(form=form))


def crash_by_user(request, username, crash_id):
    user = get_object_or_404(User, username=username)
    crash = get_object_or_404(CrashReport, user=user)
    context = dict(crash_report=crash)
    return _render(request, 'crashes/user_crash.html', context)


def crashes_by_user(request, username):
    user = get_object_or_404(User, username=username)
    crashes = CrashReport.objects.filter(user=user)
    context = dict(crash_reports=crashes)
    return _render(request, 'crashes/user_crashes.html', context)

