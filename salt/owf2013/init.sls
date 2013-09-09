include:
    - nginx
    - uwsgi


website-root:
    file:
        - directory
        - name: /srv/owf2013/
        - user: www-data
        - group: www-data
        - recurse:
            - user
            - group
        - mode: 755
        - makedirs: true


website-git:
    git.latest:
        - name: https://github.com/OWF/owf2013.git
        - rev: master
        - target: /srv/owf2013/
        - force: true
        - require:
            - pkg: git


website-virtualenv:
    virtualenv.manage:
        - name: /srv/owf2013-env/
        - requirements: /srv/owf2013/deps.txt
        - clear: false
        - require:
            - pkg: python-virtualenv


#
# uwsgi
#
uwsgi:
  pkg:
    - installed
  service:
    - running
    - watch:
      - file: /etc/uwsgi/apps-enabled/owf2013.ini

uwsgi-app:
    file.managed:
        - name: /etc/uwsgi/apps-enabled/owf2013.ini
        - source: salt://owf2013/uwsgi.ini
        - require:
            - pkg: uwsgi


#
# Nginx
#
nginx:
  pkg:
    - installed
  service:
    - running
    - watch:
      - file: /etc/nginx/sites-enabled/owf2013.conf
  file.absent:
    - name: /etc/nginx/sites-enabled/default


nginx-conf:
    file.managed:
        - name: /etc/nginx/sites-enabled/owf2013.conf
        - source: salt://owf2013/nginx.conf
        - require:
            - pkg: nginx
