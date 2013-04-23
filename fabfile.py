from fabric.api import local, task

HEROKU_APP = 'crashula'

@task
def test():
    local('py.test')

@task
def deploy():
    test()
    local('heroku maintenance:on -a {0}'.format(HEROKU_APP))
    local('git push heroku master')
    local('heroku run -a {0} python manage.py syncdb'.format(HEROKU_APP))
    local('heroku run -a {0} python manage.py migrate'.format(HEROKU_APP))
    local('heroku maintenance:off -a {0}'.format(HEROKU_APP))



