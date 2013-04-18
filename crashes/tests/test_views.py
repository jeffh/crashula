import json

import pytest

from django.http import Http404
from django.contrib.auth.models import AnonymousUser

from crashes import views as v
from crashes import factories as f
from crashes import models

@pytest.fixture
def guest():
    return AnonymousUser()

@pytest.fixture
def user(db):
    return f.UserFactory.create()

@pytest.fixture
def admin(db):
    return f.AdminFactory.create()

@pytest.fixture
def crash_report(user):
    return f.CrashReportFactory.create(user=user)

@pytest.fixture
def crash_reports(user):
    return f.CrashReportFactory.create_batch(10, user=user)

@pytest.fixture
def version(db):
    return f.VersionFactory.create()

def assert_redirects_to(response, path='/login/'):
    assert response.status_code == 302
    assert response['Location'].startswith(path)

def assert_raises_exception(view, args, exception):
    try:
        response = view(*args)
        assert 0, 'Expected {0!r}'.format(exception)
    except exception:
        pass

def assert_json(response, obj):
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    assert json.loads(response.content) == obj

# INDEX PAGE

def test_guest_user_shows_page_with_login_link(rf, guest):
    request = rf.get('/')
    request.user = guest
    response = v.index(request)
    assert response.status_code == 200
    assert '/login/' in response.content

def test_logged_in_user_redirects_to_his_or_her_crashes(rf, user):
    request = rf.get('/')
    request.user = user
    response = v.index(request)
    assert_redirects_to(response, '/crashes/u/{0}/'.format(user.username))


# AJAX VERSIONS

def test_fetch_versions(rf, user):
    app1 = f.ApplicationFactory(name='MyApp', company__name='Foo')
    app2 = f.ApplicationFactory(name='MyOtherApp', company=None)
    ver1 = f.VersionFactory(application=app1)
    ver2 = f.VersionFactory(application=app1)
    ver3 = f.VersionFactory(application=app2)

    request = rf.get('/versions/')
    request.user = user
    response = v.versions(request)
    assert_json(response, [
        dict(name='MyApp', company='Foo', versions=[
            dict(marketing=ver2.marketing, build=ver2.build),
            dict(marketing=ver1.marketing, build=ver1.build),
        ]),
        dict(name='MyOtherApp', company=None, versions=[
            dict(marketing=ver3.marketing, build=ver3.build),
        ]),
    ])

def test_fetch_version_fails_with_guest_user(rf, guest):
    request = rf.get('/versions/')
    request.user = guest
    response = v.versions(request)
    assert response.status_code != 200


# NEW CRASH PAGE - GET

def test_logged_in_user_can_see_new_crash_form(rf, user):
    request = rf.get('/crashes/new/')
    request.user = user
    response = v.new_crash(request)
    assert response.status_code == 200

def test_guest_user_gets_redirected_to_login(rf, guest):
    request = rf.get('/crashes/new/')
    request.user = guest
    response = v.new_crash(request)
    assert_redirects_to(response, '/login/?next=/crashes/new/')


# NEW CRASH PAGE - POST

def test_creating_a_crash_report_requires_title_field(rf, user, version):
    data = f.CrashReportFactory.attributes()
    data['title'] = ''
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request)
    assert response.status_code == 200
    assert models.CrashReport.objects.count() == 0

def test_creating_a_crash_report_requires_details_field(rf, user, version):
    data = f.CrashReportFactory.attributes()
    data['details'] = ''
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request)
    assert response.status_code == 200
    assert models.CrashReport.objects.count() == 0

def test_creating_a_crash_report_requires_count_to_be_greater_than_0(rf, user, version):
    data = f.CrashReportFactory.attributes()
    data['count'] = '0'
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request)
    assert response.status_code == 200
    assert models.CrashReport.objects.count() == 0


def test_logged_in_user_can_create_a_new_crash_report(rf, user, version):
    data = f.CrashReportFactory.attributes()
    data['version_id'] = version.id
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request)
    crash = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/crashes/u/{0}/{1}/'.format(user.username, crash.id))
    assert crash.title == data['title']
    assert crash.details == data['details']
    assert crash.version == version

def test_guest_user_cannot_create_a_new_crash_report(rf, db, guest):
    data = f.CrashReportFactory.attributes()
    request = rf.post('/crashes/new/', data=data)
    request.user = guest
    response = v.new_crash(request)
    assert_redirects_to(response, '/login/?next=/crashes/new/')

# LIST CRASH PAGE

def test_crash_by_user_returns_page(rf, user, crash_report):
    request = rf.get('/crashes/u/{0}/{1}/'.format(user.username, crash_report.id))
    response = v.crash_by_user(request, user.username, crash_report.id)
    assert response.status_code == 200
    assert crash_report.title in response.content

def test_crash_by_invalid_crash_id_is_a_404(rf, user):
    request = rf.get('/crashes/u/{0}/1/'.format(user.username))
    assert_raises_exception(v.crash_by_user, [request, user.username, 1], Http404)

def test_crash_by_invalid_username_is_a_404(rf, db):
    request = rf.get('/crashes/u/invalid/1/')
    assert_raises_exception(v.crash_by_user, [request, 'invalid', 1], Http404)

# LIST CRASHES PAGE

def test_anyone_can_see_crashes_by_user(rf, user, crash_reports):
    request = rf.get('/crashes/u/{0}/'.format(user.username))
    response = v.crashes_by_user(request, user.username)
    assert response.status_code == 200
    for crash_report in crash_reports:
        assert crash_report.title in response.content

def test_logged_in_user_has_link_to_add_crashes_on_users_own_page(rf, user):
    request = rf.get('/crashes/u/{0}/'.format(user.username))
    request.user = user
    response = v.crashes_by_user(request, user.username)
    assert '/crashes/new/'.format(user.username) in response.content

def test_crashes_by_invalid_username_is_a_404(rf, db):
    request = rf.get('/crashes/u/invalid/')
    assert_raises_exception(v.crashes_by_user, [request, 'invalid'], Http404)

