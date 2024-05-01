import os
from . import __version__

# Lampsible
# ---------
LAMPSIBLE_BANNER = """\
      _                           _ _     _
     | |                         (_) |   | |
     | | __ _ _ __ ___  _ __  ___ _| |__ | | ___
     | |/ _` | '_ ` _ \| '_ \/ __| | '_ \| |/ _ \\
     | | (_| | | | | | | |_) \__ \ | |_) | |  __/
     |_|\__,_|_| |_| |_| .__/|___/_|_.__/|_|\___|
                       | |
                       |_|
     --------------------------------------------
        LAMP stacks with Ansible  -  v{}
     --------------------------------------------
""".format(__version__)
SUPPORTED_ACTIONS = [
    # LAMP-Stack basics
    'lamp-stack',
    'apache',
    'mysql',
    'php',
    # PHP CMS
    'wordpress',
    # PHP frameworks
    'laravel',
    # Local debugging
    'dump-ansible-facts',
]

# Script paths
# ------------
USER_HOME_DIR            = os.path.expanduser('~')
DEFAULT_PRIVATE_DATA_DIR = os.path.join(USER_HOME_DIR, '.lampsible')
# If the user does not supply a value, this will be overwritten by a path
# inside the package installation, which we detect later on.
DEFAULT_PROJECT_DIR      = ''

# Apache
# ------
DEFAULT_APACHE_VHOST_NAME = '000-default'
DEFAULT_APACHE_SERVER_NAME = 'localhost'
DEFAULT_APACHE_SERVER_ADMIN = 'webmaster@localhost'
DEFAULT_APACHE_DOCUMENT_ROOT = '/var/www/html'

# Database
# --------
DEFAULT_DATABASE_ENGINE       = 'mysql'
DEFAULT_DATABASE_USERNAME     = 'db-username'
DEFAULT_DATABASE_HOST         = 'localhost'
DEFAULT_DATABASE_TABLE_PREFIX = ''

# PHP
# ---
DEFAULT_PHP_VERSION = '8.2'

# WordPress
# ---------
DEFAULT_WORDPRESS_VERSION        = 'latest'
DEFAULT_WORDPRESS_LOCALE         = 'en_US'
DEFAULT_WORDPRESS_SITE_TITLE     = 'Sample Site'
DEFAULT_WORDPRESS_ADMIN_USERNAME = 'admin'
DEFAULT_WORDPRESS_ADMIN_EMAIL    = 'admin@example.com'

# Web applications
# ----------------
DEFAULT_LARAVEL_ARTISAN_COMMANDS = [
    'key:generate',
    'migrate',
    'db:seed',
]

# Misc
# ----
INSECURE_CLI_PASS_WARNING = 'It\'s insecure to pass passwords via CLI args! If you are sure that you want to do this, rerun this command with the --insecure-cli-password flag.'
