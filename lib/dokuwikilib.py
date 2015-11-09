import sys
from os import path, makedirs
from shutil import rmtree
from charmhelpers.core import hookenv
from hashlib import sha256
from shell import shell

from nginxlib import get_app_path


def download_archive():
    """
    Downloads dokuwiki
    http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz
    """
    # Get the nginx vhost application path
    app_path = get_app_path()

    config = hookenv.config()
    shell('rm /tmp/dokuwiki.zip || true')
    cmd = ('wget -q -O /tmp/dokuwiki.tgz '
           'http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz')
    hookenv.log("Downloading Dokuwiki: {}".format(cmd))
    shell(cmd)

    with open('/tmp/dokuwiki.tgz', 'rb') as fp:
        dl_byte = sha256(fp.read())
        if dl_byte.hexdigest() != config['checksum']:
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
    shell(cmd)


def start():
    shell('service php5-fpm start')


def stop():
    shell('service php5-fpm stop')


def restart():
    shell('service php5-fpm restart')
