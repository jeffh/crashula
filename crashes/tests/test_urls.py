from crashes.tests.fixtures import *


def test_login_url(client, db):
    assert client.get('/login/').status_code == 200

def test_index(client, db):
    assert client.get('/').status_code == 200

def test_crashes_by_user(client, db, user):
    assert client.get('/crashes/u/{0}/'.format(user.username)).status_code == 200

def test_crash_by_user(client, db, user, crash_report):
    assert client.get('/crashes/u/{0}/{1}/'.format(user.username, crash_report.id)).status_code == 200
