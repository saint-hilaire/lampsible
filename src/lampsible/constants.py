import os

# SCRIPT PATHS
USER_HOME_DIR            = os.path.expanduser('~')
DEFAULT_PRIVATE_DATA_DIR = os.path.join(USER_HOME_DIR, '.lampsible')
# If the user does not supply a value, this will be overwritten by a path
# inside the package installation, which we detect later on.
DEFAULT_PROJECT_DIR      = ''

# APACHE
DEFAULT_APACHE_VHOST_NAME = '000-default'
DEFAULT_APACHE_SERVER_NAME = 'localhost'
DEFAULT_APACHE_SERVER_ADMIN = 'webmaster@localhost'
DEFAULT_APACHE_DOCUMENT_ROOT = '/var/www/html'

# DATABASE
DEFAULT_DATABASE_ENGINE       = 'mysql'
DEFAULT_DATABASE_USERNAME     = 'db-username'
DEFAULT_DATABASE_HOST         = 'localhost'
DEFAULT_DATABASE_TABLE_PREFIX = ''

