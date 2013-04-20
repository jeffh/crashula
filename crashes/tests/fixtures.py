import pytest
import selenium.webdriver

from django.contrib.auth.models import AnonymousUser

from crashes import factories as f

@pytest.fixture(scope='session')
def webdriver(request, live_server):
    "Returns a selenium webdriver used during the test session."
    driver = selenium.webdriver.Firefox()
    def close_driver():
        driver.close()
    request.addfinalizer(close_driver)
    return driver

@pytest.fixture()
def browser(webdriver):
    "Returns the webdriver with all its cookies cleared."
    webdriver.delete_all_cookies()
    return webdriver

@pytest.fixture()
def guest():
    "Returns an anonymous user"
    return AnonymousUser()

@pytest.fixture()
def application(db):
    "Returns an application"
    return f.ApplicationFactory.create()

@pytest.fixture()
def user(db):
    "Returns a new authenticated user in the database."
    return f.UserFactory.create()

@pytest.fixture()
def other_user(db):
    "Returns a new authenticated user in the database."
    return f.UserFactory.create()

@pytest.fixture()
def admin(db):
    "Returns a new admin user in the database."
    return f.AdminFactory.create()

@pytest.fixture()
def crash_report(user, application):
    "Returns a new crash report, with the user fixture as the owner."
    return f.CrashReportFactory.create(user=user, application=application)

@pytest.fixture()
def crash_reports(user, application):
    "Returns 10 crash reports, with the user fixture as the owner."
    return f.CrashReportFactory.create_batch(10, user=user, application=application)
