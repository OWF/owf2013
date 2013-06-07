from fabric.api import *

from fabtools import require
from fabtools.python import virtualenv
import time

# Config
env.user = 'fermigier'
env.group = 'fermigier'
env.hosts = ['dedibox']
env.hostname = ''

#env.user = 'owf'
#env.group = 'owf'
#env.hosts = ['openwf.nexen.net']
#env.hostname = ''


env.app_name = local('python setup.py --name', capture=True).strip()
env.app_root = '/home/{}/websites/{}'.format(env.user, env.app_name)
env.app_env = '/home/{}/websites/envs/{}'.format(env.user, env.app_name)


UWSGI_CONFIG_TPL = """
[uwsgi]
uid = %(user)s
gid = %(group)s
chdir = %(app_root)s
virtualenv = %(app_env)s
socket = uwsgi.sock
chmod-socket = 666
pythonpath = .
wsgi-file = wsgi.py
callable = app
plugins = python
processes = 4
threads = 2
"""

# Not used yet.
NGINX_CONFIG_TPL = """
erver {
  server_name owf2013.demo.abilian.com;
  server_name www.openworldforum.org openworldforum.org;

  access_log /var/log/nginx/owf2013-access.log;

  location /static/ {
    root /home/fermigier/websites/owf2013/website;
  }

  location / { try_files $uri @owf2013; }
  location @owf2013 {
    include uwsgi_params;
    uwsgi_pass unix:/home/fermigier/websites/owf2013/uwsgi.sock;
  }

}
"""

@task
def setup():
  require.python.virtualenv(env.app_env)
  require.files.directory(env.app_root)


@task
def install_deps():
  with cd(env.app_root):
    put("deps.txt", "deps.txt")
    with virtualenv(env.app_env):
      require.python.install_requirements("deps.txt")


@task
def refresh_uwsgi():
  require.file("/etc/uwsgi/apps-available/%s.ini" % env.app_name,
               contents=UWSGI_CONFIG_TPL % {
                 'user': env.user,
                 'group': env.group,
                 'app_root': env.app_root,
                 'app_env': env.app_env,
               }, use_sudo=True)
  sudo("ln -sf /etc/uwsgi/apps-available/%s.ini "
       "/etc/uwsgi/apps-enabled/%s.ini" % (env.app_name, env.app_name))
  require.service.restarted('uwsgi')


@task
def pack():
  # create a new source distribution as tarball
  local('python setup.py sdist --formats=gztar', capture=False)


@task
def backup():
  with cd(env.app_root):
    now = time.strftime("%Y%m%d-%H%M%S")
    run("cp feedback.csv ~/backup/lemooc-feedback-{}.csv".format(now))
    run("cp data/lemooc.db ~/backup/lemooc-db-{}.db".format(now))


@task
def deploy():
  # figure out the release name and version
  dist = local('python setup.py --fullname', capture=True).strip()

  # upload the source tarball to the temporary folder on the server
  put('dist/{}.tar.gz'.format(dist), '/tmp/{}.tar.gz'.format(dist))

  # create a place where we can unzip the tarball, then enter
  # that directory and unzip it
  with cd("/tmp"):
    run('rm -rf {}/*'.format(dist))
    run('tar xzf /tmp/{}.tar.gz'.format(dist))
    with cd(dist):
      run("tox")

  run("cp -r /tmp/{}/* {}".format(dist, env.app_root))

  install_deps()
  with cd(env.app_root):
    with virtualenv(env.app_env):
      run("py.test")

  with cd(env.app_root):
    with virtualenv(env.app_env):
      run("make index")

  refresh_uwsgi()

  run('rm -f /tmp/{}.tar.gz'.format(dist))


@task(default=True)
def default():
  pack()
  #backup()
  deploy()
