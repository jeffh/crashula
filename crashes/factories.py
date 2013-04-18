import factory
from django.contrib.auth.models import User

from crashes.models import *


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    first_name = 'John'
    last_name = 'Doe'
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    is_staff = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = 'test123'
        if 'password' in kwargs:
            password = kwargs.pop('password')
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        user.set_password(password)
        if create:
            user.save()
        return user

class AdminFactory(UserFactory):
    first_name = 'Bruce'
    last_name = 'Wayne'
    username = factory.Sequence(lambda n: 'admin{0}'.format(n))
    is_staff = True

class CompanyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Company

    name = factory.Sequence(lambda n: 'Company {0}'.format(n))

class ApplicationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Application

    name = factory.Sequence(lambda n: 'Application {0}'.format(n))
    company = factory.SubFactory(CompanyFactory)

class VersionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Version

    application = factory.SubFactory(ApplicationFactory)
    marketing = factory.Sequence(lambda n: 'Marketing Version {0}'.format(n))
    build = factory.Sequence(lambda n: n)

class CrashReportFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CrashReport

    version = factory.SubFactory(VersionFactory)
    user = factory.SubFactory(UserFactory)
    details = factory.Sequence(lambda n: 'CrashReport Details {0}'.format(n))
    title = factory.Sequence(lambda n: 'CrashReport Title {0}'.format(n))
    count = 1

