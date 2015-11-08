from charms.reactive import (
    hook,
    when,
    only_once,
    is_state
)

from charmhelpers.core import hookenv, host
from shell import shell

# ./lib/nginxlib
import nginxlib

# ./lib/dokuwikilib.py
import dokuwikilib

config = hookenv.config()


# HOOKS -----------------------------------------------------------------------
@hook('config-changed')
def config_changed():

    if not is_state('nginx.available'):
        return

    dokuwikilib.restart()
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
    nginxlib.configure_site('default', 'vhost.conf')

    # Update application
    dokuwikilib.download_archive()

    # Fix php5 cgi.fix_pathinfo
    shell("sed 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' "
          "/etc/php5/fpm/php.ini")

    dokuwikilib.restart()
    host.service_restart('nginx')
    hookenv.status_set('active', 'Dokuwiki is installed!')
