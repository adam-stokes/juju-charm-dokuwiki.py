from charms.reactive import (
    hook,
    when,
    only_once,
    is_state
)

import os.path as path
from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from subprocess import call
from charms.layer import nginx, dokuwiki

config = hookenv.config()


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
    call('chmod 775 -R {}/data'.format(app_path), shell=True)

    dokuwiki.restart()
    host.service_restart('nginx')
    hookenv.status_set('active', 'Ready')


# REACTORS --------------------------------------------------------------------
@when('nginx.available')
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

    # Fix php5 cgi.fix_pathinfo
    call(
        "sed 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' "
        "/etc/php/7.0/fpm/php.ini", shell=True)

    dokuwiki.restart()
    host.service_restart('nginx')
    hookenv.status_set('active', 'Dokuwiki is installed!')
