import json

from django.http import Http404

from crashes import views as v
from crashes import factories as f
from crashes import models
from crashes.tests.fixtures import *

def assert_redirects_to(response, path='/login/'):
    assert response.status_code == 302, 'assert redirect 302, got {0} with {1}'.format(response.status_code, response.content)
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

#def test_integration(live_server, browser):
#    browser.get(unicode(live_server))
#    assert 'Crashula' in browser.title

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
    assert_redirects_to(response, '/u/{0}/'.format(user.username))


# NEW CRASH PAGE - GET

def test_logged_in_user_can_see_new_crash_form(rf, user):
    request = rf.get('/crashes/new/')
    request.user = user
    response = v.new_crash(request, request.user.username)
    assert response.status_code == 200

def test_guest_user_gets_redirected_to_login(rf, guest):
    request = rf.get('/crashes/new/')
    request.user = guest
    response = v.new_crash(request, request.user.username)
    assert_redirects_to(response, '/login/?next=/crashes/new/')


# NEW CRASH PAGE - POST

def test_creating_a_crash_report_requires_validation(rf, user, application):
    # see CrashForm test for more validation
    data = f.CrashReportFactory.attributes()
    data['title'] = ''
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request, request.user.username)
    assert response.status_code == 200
    assert models.CrashReport.objects.count() == 0

def test_logged_in_user_can_create_a_new_crash_with_existing_crash_report(rf, user, application):
    data = f.CrashReportFactory.attributes()
    del data['application']
    del data['user']
    crash_report = f.CrashReportFactory.create(user=user, application=application, **data)
    data['application'] = application.id
    request = rf.post('/crashes/new/', data=data)
    request.user = user

    response = v.new_crash(request, user)

    crash_report = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert models.CrashReport.objects.count() == 1
    assert crash_report.title == data['title']
    assert crash_report.details == data['details']
    assert crash_report.version == data['version']
    assert crash_report.application == application
    assert crash_report.count == 2

def test_logged_in_user_can_create_a_new_crash_and_crash_report(rf, user, application):
    data = f.CrashReportFactory.attributes()
    data['application'] = application.id
    request = rf.post('/crashes/new/', data=data)
    request.user = user
    response = v.new_crash(request, user)
    crash_report = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert crash_report.title == data['title']
    assert crash_report.details == data['details']
    assert crash_report.application == application
    assert crash_report.count == 1

def test_guest_user_cannot_create_a_new_crash_report(rf, db, guest):
    data = f.CrashReportFactory.attributes()
    request = rf.post('/crashes/new/', data=data)
    request.user = guest
    response = v.new_crash(request, guest)
    assert_redirects_to(response, '/login/?next=/crashes/new/')

# CRASH PAGE

def test_crash_by_user_returns_page(rf, user, crash_reports):
    request = rf.get('/u/{0}/{1}/'.format(user.username, crash_reports[0].id))
    response = v.crash_by_user(request, user.username, crash_reports[0].id)
    assert response.status_code == 200
    assert crash_reports[0].title in response.content

def test_crash_by_invalid_crash_id_is_a_404(rf, user):
    request = rf.get('/u/{0}/1/'.format(user.username))
    assert_raises_exception(v.crash_by_user, [request, user.username, 1], Http404)

def test_crash_by_invalid_username_is_a_404(rf, db):
    request = rf.get('/u/invalid/1/')
    assert_raises_exception(v.crash_by_user, [request, 'invalid', 1], Http404)


# EDIT CRASH PAGE - GET

def test_user_that_owns_the_crash_report_can_edit(rf, user, crash_report):
    request = rf.get('/crashes/{0}/'.format(crash_report.id))
    request.user = user
    response = v.edit_crash(request, request.user.username, crash_report.id)
    assert response.status_code == 200

def test_editing_crash_report_requires_login(rf, guest, crash_report):
    request = rf.get('/crashes/{0}/'.format(crash_report.id))
    request.user = guest
    response = v.edit_crash(request, request.user.username, crash_report.id)
    assert_redirects_to(response, '/login/?next=/crashes/{0}/'.format(crash_report.id))

def test_editing_non_existant_crash_report_is_a_404(rf, user):
    request = rf.get('/crashes/2/')
    request.user = user
    assert_raises_exception(v.edit_crash, [request, user.username, 2], Http404)

def test_other_users_cannot_edit_crash_reports(rf, user, other_user, crash_report):
    request = rf.get('/crashes/{0}/'.format(crash_report.id))
    request.user = other_user
    assert_raises_exception(v.edit_crash, [request, request.user.username, crash_report.id], Http404)

# EDIT CRASH PAGE - PUT

def test_logged_in_user_can_update_a_crash_report(rf, user, application, crash_report):
    data = f.CrashReportFactory.attributes()
    data['application'] = application.id
    request = rf.post('/u/{0}/{1}/edit/'.format(user.username, crash_report.id), data=data)
    request.user = user
    response = v.edit_crash(request, request.user.username, crash_report.id)

    crash_report = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert models.CrashReport.objects.count() == 1
    assert crash_report.title == data['title']
    assert crash_report.details == data['details']
    assert crash_report.application == application


# LIST CRASHES PAGE

def test_anyone_can_see_crashes_by_user(rf, user, crash_reports):
    request = rf.get('/u/{0}/'.format(user.username))
    response = v.crashes_by_user(request, user.username)
    assert response.status_code == 200

def test_crashes_by_invalid_username_is_a_404(rf, db):
    request = rf.get('/u/invalid/')
    assert_raises_exception(v.crashes_by_user, [request, 'invalid'], Http404)

