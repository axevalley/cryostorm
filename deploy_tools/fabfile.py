from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/axevalley/cryostorm.git'


def deploy():
    site_folder = '/home/{}/sites/{}/'.format(env.user, env.host)
    source_folder = ''.join([site_folder, '/source'])
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _add_local_settings(source_folder)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('static', 'virtualenv', 'source'):
        run('mkdir -p {}/{}'.format(site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(''.join([source_folder, '/.git'])):
        run('cd {} && git fetch'.format(source_folder))
    else:
        run('git clone {} {}'.format(REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {} && git reset --hard {}'.format(source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/cryostorm/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(
        settings_path, 'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["{}"]'.format(site_name))
    secret_key_file = source_folder + '/cryostorm/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!"@#$%^&*"'
        key = ''.join([random.SystemRandom().choice(chars) for _ in range(50)])
        append(secret_key_file, "SECRET_KEY = '{}'".format(key,))
    append(settings_path, '\nfrom . secret_key import SECRET_KEY')


def _add_local_settings(source_folder):
    local_settings_file = source_folder + '/cryostorm/local_settings.py'
    if not exists(local_settings_file):
        host = input('Database Host: ')
        name = input('Database Name: ')
        test_name = input('Test Database Name: ')
        user = input('Database User: ')
        password = input('Database Password: ')

        append(local_settings_file, 'DATABASES = {')
        append(local_settings_file, "    'default': {")
        append(
            local_settings_file,
            "        'ENGINE': 'django.db.backends.postgresql',")
        append(local_settings_file, "        'HOST': '{}',".format(host))
        append(local_settings_file, "        'NAME': '{}',".format(name))
        append(
            local_settings_file,
            "        'TEST_NAME': '{}',".format(test_name))
        append(local_settings_file, "        'USER': '{}',".format(user))
        append(
            local_settings_file,
            "        'PASSWORD': '{}',".format(password))
        append(local_settings_file, "        'PORT': '5432',")
        append(local_settings_file, '    }')
        append(local_settings_file, '}')


def _update_virtualenv(source_folder):
    virtualenv_folder = '/'.join([source_folder, '..', 'virtualenv'])
    if not exists('/'.join([virtualenv_folder, 'bin', 'pip'])):
        run('python3 -m venv {}'.format(virtualenv_folder))
    run('{}/bin/pip install -r {}/requirements.txt'.format(
        virtualenv_folder, source_folder))


def _update_static_files(source_folder):
    run(
        'cd {} && ../virtualenv/bin/python manage.py collectstatic \
        --noinput'.format(source_folder))


def _update_database(source_folder):
    run(
        'cd {} && ../virtualenv/bin/python manage.py migrate \
        --noinput'.format(source_folder))
