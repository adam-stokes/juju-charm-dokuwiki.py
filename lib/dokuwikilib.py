import sys
from os import path, makedirs
from shutil import rmtree
from charmhelpers.core import hookenv
from hashlib import sha256
from shell import shell


def download_archive():
    """
    Downloads dokuwiki
    http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz
    """
    config = hookenv.config()
    shell('rm /tmp/dokuwiki.zip || true')
    cmd = ('wget -q -O /tmp/dokuwiki.zip '
           'http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz')
    hookenv.log("Downloading Dokuwiki: {}".format(cmd))
    shell(cmd)

    with open('/tmp/dokuwiki.zip', 'rb') as fp:
        dl_byte = sha256(fp.read())
        if dl_byte.hexdigest() != config['checksum']:
            hookenv.status_set(
                'blocked',
                'Downloaded Dokuwiki checksums do not match, '
                'possibly because of a new stable release. '
                'Check dokuwiki.org!')
            sys.exit(0)

    if path.isdir(config['app-path']):
        rmtree(config['app-path'])
    makedirs(config['app-path'])

    cmd = ('tar xf /tmp/dokuwiki.zip -C {} --strip-components=1'.format(
        config['app-path']
    ))
    hookenv.log("Extracting Dokuwiki: {}".format(cmd))
    shell(cmd)


def start():
    shell('service php5-fpm start')


def stop():
    shell('service php5-fpm stop')


def restart():
    shell('service php5-fpm restart')
