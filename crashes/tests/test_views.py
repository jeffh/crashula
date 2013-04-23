import json
import urlparse

from django.http import Http404

from crashes import views as v
from crashes import factories as f
from crashes import models
from crashes.tests.fixtures import *


def assert_redirects_to(response, path='/login/'):
    assert response.status_code == 302, 'assert redirect 302, got {0} with {1}'.format(response.status_code, response.content)
    uri = urlparse.urlparse(response['Location'])
    path_and_query = uri.path + '?' + uri.query
    assert path_and_query.startswith(path)

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

def test_guest_user_shows_page_with_login_link(client):
    response = client.get('/')
    assert response.status_code == 200
    assert '/login/' in response.content

def test_logged_in_user_redirects_to_his_or_her_crashes(user_client, user):
    response = user_client.get('/')
    assert_redirects_to(response, '/u/{0}/'.format(user.username))


# NEW CRASH PAGE - GET

def test_logged_in_user_can_see_new_crash_form(user_client, user):
    response = user_client.get('/u/{0}/new/'.format(user.username))
    assert response.status_code == 200

def test_guest_user_gets_redirected_to_login(client):
    response = client.get('/u/jeff/new/')
    assert_redirects_to(response, '/login/?next=/u/jeff/new/')


# NEW CRASH PAGE - POST

def test_creating_a_crash_report_requires_validation(user_client, user, application):
    # see CrashForm test for more validation
    data = f.CrashReportFactory.attributes()
    data['title'] = ''
    response = user_client.post('/u/{0}/new/'.format(user.username), data=data)
    assert response.status_code == 200
    assert models.CrashReport.objects.count() == 0


def test_logged_in_user_can_create_a_new_crash_report(user_client, user, application):
    data = f.CrashReportFactory.attributes()
    data['application'] = application.id
    response = user_client.post('/u/{0}/new/'.format(user.username), data=data)
    assert models.CrashReport.objects.count() > 0
    crash_report = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert crash_report.title == data['title']
    assert crash_report.details == data['details']
    assert crash_report.application == application
    assert crash_report.count == 1

def test_guest_user_cannot_create_a_new_crash_report(client, db):
    data = f.CrashReportFactory.attributes()
    response = client.post('/crashes/new/', data=data)
    assert response.status_code != 200

# CRASH PAGE

def test_crash_by_user_returns_page(user_client, user, crash_reports):
    response = user_client.get('/u/{0}/{1}/'.format(user.username, crash_reports[0].id))
    assert response.status_code == 200
    assert crash_reports[0].title in response.content

def test_crash_by_invalid_crash_id_is_a_404(user_client, user):
    response = user_client.get('/u/{0}/1/'.format(user.username))
    assert response.status_code == 404

def test_crash_by_invalid_username_is_a_404(client, db):
    response = client.get('/u/invalid/1/')
    assert response.status_code == 404


# EDIT CRASH PAGE - GET

def test_user_that_owns_the_crash_report_can_edit(user_client, user, crash_report):
    response = user_client.get('/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert response.status_code == 200

def test_editing_crash_report_requires_login(client, user, crash_report):
    response = client.get('/u/{0}/{1}/edit/'.format(user.username, crash_report.id))
    assert_redirects_to(response, '/login/?next=/u/{0}/{1}/'.format(user.username, crash_report.id))

def test_editing_non_existant_crash_report_is_a_404(user_client, user):
    response = user_client.get('/crashes/2/')
    assert response.status_code == 404

def test_other_users_cannot_edit_crash_reports(client, user, other_user, crash_report):
    client.login(username=other_user.username, password='password')
    response = client.get('/crashes/{0}/'.format(crash_report.id))
    assert response.status_code == 404

# EDIT CRASH PAGE - PUT

def test_logged_in_user_can_update_a_crash_report(user_client, user, application, crash_report):
    data = f.CrashReportFactory.attributes()
    data['application'] = application.id
    response = user_client.post('/u/{0}/{1}/edit/'.format(user.username, crash_report.id), data=data)

    crash_report = models.CrashReport.objects.all()[0]
    assert_redirects_to(response, '/u/{0}/{1}/'.format(user.username, crash_report.id))
    assert models.CrashReport.objects.count() == 1
    assert crash_report.title == data['title']
    assert crash_report.details == data['details']
    assert crash_report.application == application


# LIST CRASHES PAGE

def test_anyone_can_see_crashes_by_user(client, user, crash_reports):
    response = client.get('/u/{0}/'.format(user.username))
    assert response.status_code == 200
    i = 0
    sorted_crash_reports = sorted(crash_reports, cmp=lambda x, y: cmp(x.updated_at, y.updated_at))
    sorted_crash_reports.reverse()
    assert list(response.context['crash_reports']) == sorted_crash_reports

def test_crashes_by_invalid_username_is_a_404(client, db):
    response = client.get('/u/invalid/')
    assert response.status_code == 404

