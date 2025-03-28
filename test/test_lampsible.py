import os
import unittest
from getpass import getpass, getuser
from lampsible import __version__
from lampsible.lampsible import Lampsible
from lampsible.constants import *

class TestLampsible(unittest.TestCase):

    def setUp(self):
        try:
            tmp_remote = os.environ['LAMPSIBLE_REMOTE'].split('@')
            web_user = tmp_remote[0]
            web_host = tmp_remote[1]
        except IndexError:
            web_user = getuser()
            web_host = 'localhost'
        except KeyError:
            exit("Please set environment variable 'LAMPSIBLE_REMOTE'!")

        self.lampsible = Lampsible(
            web_user=web_user,
            web_host=web_host,
            action='apache',
            private_data_dir=os.path.join(
                'test',
                'tmp-private-data',
            ),
            database_root_password='rootpassword',
            database_username=DEFAULT_DATABASE_USERNAME,
            database_password='password',
            database_host=DEFAULT_DATABASE_HOST,
            ssl_test_cert=True,
            apache_server_admin='me@me.me',
            ansible_galaxy_ok=True,
        )
        if web_host in ['localhost', '127.0.0.1']:
            self.lampsible.remote_sudo_password = getpass(
                'Please enter local sudo password: '
            )


    def test_banner(self):
        self.assertIn(__version__, self.lampsible.banner)


    def test_apache(self):
        self.lampsible.set_action('apache')
        self.lampsible.ssl_certbot = False
        self._do_test_run()


    def test_ssl_selfsigned(self):
        self.lampsible.set_action('apache')
        self.lampsible.ssl_selfsigned = True
        self._do_test_run()


    def test_mysql(self):
        self.lampsible.set_action('mysql')
        self.lampsible.database_name = 'test_database'
        self._do_test_run()


    def test_simple_php(self):
        self.lampsible.set_action('php')
        self._do_test_run()


    def test_full_php(self):
        self.lampsible.set_action('php')
        # You can test this further by building a VPS with Ubuntu 20,
        # then leaving this unchanged - that should fail.
        # Then change it to 7.4, and it should work.
        # This php_version stuff is pretty cumbersome... and most of the time,
        # it can be left blank... I think I want to drop support for
        # this in the next major version.
        self.lampsible.php_version = '8.3'
        self.lampsible.php_extensions = [
            'php-mysql',
            'php-xml',
            'php-gd',
            'php-curl',
            'php-mbstring',
        ]
        self.lampsible.php_memory_limit = '512M'
        self.lampsible.php_upload_max_filesize = '8M'
        self.lampsible.php_post_max_size = '8M'
        self.lampsible.php_max_execution_time = '66'
        self.lampsible.php_max_input_time = '66'
        self.lampsible.php_max_file_uploads = '21'
        self.lampsible.php_allow_url_fopen = False
        self.lampsible.php_error_reporting = 'E_ALL'
        # Very important that this ends up 'Off' on server,
        # unless we explicitly set the following to True.
        #self.lampsible.php_display_errors = True
        self.lampsible.composer_packages = ['drush/drush', 'guzzlehttp/guzzle']
        self.lampsible.composer_project = 'drupal/recommended-project'
        self.lampsible.composer_working_directory = '/var/www/html/test-app'
        self._do_test_run()


    def test_extra_apt_packages(self):
        self.lampsible.set_action('apache')
        self.lampsible.extra_packages = ['tmux', 'neofetch']
        self._do_test_run()


    def test_lamp_stack(self):
        self.lampsible.set_action('lamp-stack')
        self.lampsible.database_name = 'test_database'
        self.lampsible.php_extensions = ['php-mysql', 'php-xml']
        self._do_test_run()


    def test_wordpress(self):
        self.lampsible.set_action('wordpress')
        self.lampsible.database_name = 'wordpress'
        self.lampsible.admin_password = 'password'
        self._do_test_run()


    def test_joomla(self):
        self.lampsible.set_action('joomla')
        self.lampsible.database_name = 'joomla'
        self.lampsible.admin_password = 'passwordpassword'
        self._do_test_run()


    def test_drupal(self):
        self.lampsible.set_action('drupal')
        self.lampsible.database_name = 'drupal'
        self.lampsible.admin_password = 'password'
        self._do_test_run()


    def test_extra_env_vars(self):
        self.lampsible.set_action('apache')
        self.lampsible.extra_env_vars = {
            'HELLO': 'world',
            'FOO'  : 'bar',

        }
        self._do_test_run()


    def test_laravel(self):
        try:
            app_build_path = os.path.abspath(
                os.environ['LAMPSIBLE_LARAVEL_PATH']
            )
            app_name = os.environ['LAMPSIBLE_LARAVEL_NAME']
        except KeyError:
            self.skipTest('Got no LAMPSIBLE_LARAVEL_PATH and LAMPSIBLE_LARAVEL_NAME')
        self.lampsible.set_action('laravel')
        self.lampsible.database_name = 'laravel'
        self.lampsible.app_build_path = app_build_path
        self.lampsible.app_name = app_name
        self.lampsible.extra_env_vars = {
            'I_SHOULD_BE_IN': '.env-and-not-in-envvars'
        }
        self._do_test_run()


    def test_suitecrm(self):
        self.lampsible.set_action('suitecrm')
        self.lampsible.database_name = 'suitecrm'
        self.lampsible.admin_password = 'password'
        # Uncomment this to test SuiteCRM 7.
        # Otherwise, it will default to version 8.
        #self.lampsible.suitecrm_version = '7'
        self.lampsible.suitecrm_demo_data = True
        self._do_test_run()


    def _do_test_run(self):
        result = self.lampsible.run()
        self.assertEqual(result, 0)


    # TODO?
    # def test_validator(self):
    #     self.assertEqual(1, 1)
