import sys
from os import path, makedirs
from shutil import rmtree
from charmhelpers.core import hookenv, host
from subprocess import call, check_call

from charms.layer.nginx import get_app_path


def download_archive():
    """
    Downloads dokuwiki
    http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz
    """
    # Get the nginx vhost application path
    app_path = get_app_path()

    config = hookenv.config()
    call('rm /tmp/dokuwiki.zip || true', shell=True)
    cmd = ('wget -q -O /tmp/dokuwiki.tgz '
           'http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz')
    hookenv.log("Downloading Dokuwiki: {}".format(cmd))
    check_call(cmd, shell=True)

    if host.file_hash('/tmp/dokuwiki.tgz', 'sha256') != config['checksum']:
        hookenv.status_set(
            'blocked',
            'Downloaded Dokuwiki checksums do not match, '
            'possibly because of a new stable release. '
            'Check dokuwiki.org!')
        sys.exit(0)

    if path.isdir(app_path):
        rmtree(app_path)
    makedirs(app_path)

    cmd = ('tar xf /tmp/dokuwiki.tgz -C {} --strip-components=1'.format(
        app_path
    ))
    hookenv.log("Extracting Dokuwiki: {}".format(cmd))
    check_call(cmd, shell=True)


def start():
    check_call('service php7.0-fpm start', shell=True)


def stop():
    check_call('service php7.0-fpm stop', shell=True)


def restart():
    check_call('service php7.0-fpm restart', shell=True)
