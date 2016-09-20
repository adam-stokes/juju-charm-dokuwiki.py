from charms.reactive import (
    hook,
    when,
    only_once,
    is_state
)

import os.path as path
from charmhelpers.core import hookenv
from charmhelpers.core.host import service_restart, lsb_release
from charmhelpers.core.templating import render
from subprocess import call
from charms.layer import nginx, dokuwiki, php

config = hookenv.config()

series = lsb_release()['DISTRIB_CODENAME']
config['fpm_sock_path'] = '/var/run/php5-fpm.sock'
if series == 'xenial':
    config['fpm_sock_path'] = '/var/run/php/php7.0-fpm.sock'


# HOOKS -----------------------------------------------------------------------
@hook('config-changed')
def config_changed():

    if not is_state('nginx.available'):
        return

    # Define user
    app_path = nginx.get_app_path()
    render(source='users.auth.php',
           target=path.join(app_path, 'conf/users.auth.php'),
           context=config, perms=0o664)
    call('chown www-data:www-data -R {}'.format(app_path), shell=True)
    call('chmod 775 -R {}/conf'.format(app_path), shell=True)
    call('mkdir -p {app_path}/data && chmod 775 -R {app_path}/data'.format(
        app_path=app_path), shell=True)

    php.restart()
    service_restart('nginx')
    hookenv.status_set('active', 'Ready')


# REACTORS --------------------------------------------------------------------
@when('nginx.available')
@when('php.ready')
@only_once
def install_app():
    """ Performs application installation
    """

    hookenv.log('Installing Dokuwiki', 'info')

    # Configure NGINX vhost
    nginx.configure_site('default', 'vhost.conf')

    # Update application
    dokuwiki.download_archive()

    # Needs to set dokuwiki directory permissions for installation
    app_path = nginx.get_app_path()

    render(source='local.php',
           target=path.join(app_path, 'conf/local.php'),
           context=config, perms=0o644)

    render(source='acl.auth.php',
           target=path.join(app_path, 'conf/acl.auth.php'),
           context=config, perms=0o644)

    render(source='plugins.local.php',
           target=path.join(app_path, 'conf/plugins.local.php'),
           context=config, perms=0o644)

    # Clean up install.php as we don't need it
    call("rm -f {}/conf/install.php", shell=True)

    php.restart()
    service_restart('nginx')
    hookenv.status_set('active', 'Dokuwiki is installed!')
