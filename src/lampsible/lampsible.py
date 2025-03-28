import os
from copy import deepcopy
from textwrap import dedent
from yaml import safe_load
from ansible_runner import (
    Runner, RunnerConfig, run_command, run as ansible_runner_run
)
from ansible_directory_helper.private_data import PrivateData
from fqdn import FQDN
from .constants import *


class Lampsible:

    def __init__(self, web_user, web_host, action,
            private_data_dir=DEFAULT_PRIVATE_DATA_DIR,
            apache_server_admin=DEFAULT_APACHE_SERVER_ADMIN,
            database_root_password=None,
            database_username=None,
            database_name=None, database_host=None, database_system_user=None,
            database_system_host=None,
            php_version=DEFAULT_PHP_VERSION,
            site_title=DEFAULT_SITE_TITLE,
            admin_username=DEFAULT_ADMIN_USERNAME, admin_email=DEFAULT_ADMIN_EMAIL,
            wordpress_version=DEFAULT_WORDPRESS_VERSION,
            wordpress_locale=DEFAULT_WORDPRESS_LOCALE,
            joomla_version=DEFAULT_JOOMLA_VERSION,
            joomla_admin_full_name=DEFAULT_JOOMLA_ADMIN_FULL_NAME,
            drupal_profile=DEFAULT_DRUPAL_PROFILE,
            app_name=None,
            app_build_path=None,
            ssl_certbot=True,
            ssl_selfsigned=False, remote_sudo_password=None,
            ssh_key_file=None, apache_vhost_name=DEFAULT_APACHE_VHOST_NAME,
            apache_document_root=DEFAULT_APACHE_DOCUMENT_ROOT,
            database_password=None,
            database_table_prefix=DEFAULT_DATABASE_TABLE_PREFIX,
            php_extensions=[],
            # TODO: In a future version, it should be possible to make these
            # settings default to None, and then dynamically exclude them from the
            # vars_file, and let the third party role fall back to its own
            # defaults.
            php_memory_limit=DEFAULT_PHP_MEMORY_LIMIT,
            php_upload_max_filesize=DEFAULT_PHP_UPLOAD_MAX_FILESIZE,
            php_post_max_size=DEFAULT_PHP_POST_MAX_SIZE,
            php_max_execution_time=DEFAULT_PHP_MAX_EXECUTION_TIME,
            php_max_input_time=DEFAULT_PHP_MAX_INPUT_TIME,
            php_max_file_uploads=DEFAULT_PHP_MAX_FILE_UPLOADS,
            php_allow_url_fopen=DEFAULT_PHP_ALLOW_URL_FOPEN,
            php_error_reporting=DEFAULT_PHP_ERROR_REPORTING,
            php_display_errors=DEFAULT_PHP_DISPLAY_ERRORS,
            composer_packages=[], composer_working_directory=None,
            composer_project=None, admin_password=None,
            wordpress_insecure_allow_xmlrpc=False,
            app_local_env=False,
            laravel_artisan_commands=DEFAULT_LARAVEL_ARTISAN_COMMANDS,
            suitecrm_version=DEFAULT_SUITECRM_VERSION,
            suitecrm_demo_data=False,
            email_for_ssl=None,
            domains_for_ssl=[], ssl_test_cert=False,
            extra_packages=[], extra_env_vars={},
            apache_custom_conf_name='',
            ansible_galaxy_ok=False,
            # TODO: Lots of room for improvement for this one.
            # For now, just adding it so we can keep the interactive prompt
            # about installing missing Galaxy Collections, otherwise, it would
            # be annoying for the user to have to rerun from the beginning.
            # But "interactive Lampsible" could be a big feature, perhaps something
            # for v3.
            interactive=False,
            ):

        self.web_user = web_user
        self.web_host = web_host

        if database_system_user:
            self.database_system_user = database_system_user
        else:
            self.database_system_user = self.web_user
        if database_system_host:
            self.database_system_host = database_system_host
        else:
            self.database_system_host = self.web_host

        self.private_data_helper = PrivateData(private_data_dir)
        self._init_inventory()

        self.runner_config = RunnerConfig(
            private_data_dir=private_data_dir,
            project_dir=PROJECT_DIR,
        )

        self.runner = Runner(config=self.runner_config)

        self.apache_document_root = apache_document_root
        self.apache_vhost_name    = apache_vhost_name
        self.apache_server_admin  = apache_server_admin

        self.ssl_certbot     = ssl_certbot
        self.ssl_test_cert   = ssl_test_cert
        self.ssl_selfsigned  = ssl_selfsigned
        self.email_for_ssl   = email_for_ssl
        self.domains_for_ssl = domains_for_ssl

        self.apache_custom_conf_name = apache_custom_conf_name

        self.database_root_password = database_root_password
        self.database_username      = database_username
        self.database_password      = database_password
        self.database_name          = database_name
        self.database_host          = database_host
        self.database_table_prefix  = database_table_prefix

        self.php_version             = php_version
        self.php_extensions          = php_extensions
        self.php_memory_limit        = php_memory_limit
        self.php_upload_max_filesize = php_upload_max_filesize
        self.php_post_max_size       = php_post_max_size
        self.php_max_execution_time  = php_max_execution_time
        self.php_max_input_time      = php_max_input_time
        self.php_max_file_uploads    = php_max_file_uploads
        self.php_allow_url_fopen     = php_allow_url_fopen
        self.php_error_reporting     = php_error_reporting
        self.php_display_errors      = php_display_errors

        self.composer_packages          = composer_packages
        self.composer_project           = composer_project
        self.composer_working_directory = composer_working_directory

        self.site_title     = site_title
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.admin_email    = admin_email

        self.wordpress_version = wordpress_version
        self.wordpress_locale  = wordpress_locale
        self.wordpress_insecure_allow_xmlrpc  = wordpress_insecure_allow_xmlrpc

        self.joomla_version = joomla_version
        self.joomla_admin_full_name = joomla_admin_full_name

        self.drupal_profile = drupal_profile

        self.app_name = app_name
        self.app_build_path = app_build_path
        self.laravel_artisan_commands = laravel_artisan_commands
        self.app_local_env = app_local_env

        self.suitecrm_version   = suitecrm_version
        self.suitecrm_demo_data = suitecrm_demo_data

        self.extra_packages = extra_packages
        self.extra_env_vars = extra_env_vars

        if ssh_key_file:
            try:
                with open(os.path.abspath(ssh_key_file), 'r') as key_file:
                    key_data = key_file.read()
                self.runner_config.ssh_key_data = key_data
            except FileNotFoundError:
                print('Warning! SSH key file not found!')

        self.remote_sudo_password = remote_sudo_password

        self.banner = LAMPSIBLE_BANNER
        self.ansible_galaxy_ok = ansible_galaxy_ok
        self.interactive = interactive

        self.set_action(action)


    def set_action(self, action):
        self.action = action

        try:
            required_php_extensions = [
                'php-{}'.format(
                    extension
                ) for extension in REQUIRED_PHP_EXTENSIONS[self.action]
            ]
        except KeyError:
            required_php_extensions = []

        if action == 'wordpress':
            if self.database_table_prefix == DEFAULT_DATABASE_TABLE_PREFIX:
                self.database_table_prefix = 'wp_'
        elif action == 'drupal':
            if not self.composer_project:
                self.composer_project = 'drupal/recommended-project'
            if not self.composer_working_directory:
                self.composer_working_directory = '{}/drupal'.format(
                    self.apache_document_root
                )
            try:
                if 'drush/drush' not in self.composer_packages:
                    self.composer_packages.append('drush/drush')
            except AttributeError:
                self.composer_packages = ['drush/drush']
        elif action == 'suitecrm':
            self.extra_packages.append('unzip')

        for ext in required_php_extensions:
            if ext not in self.php_extensions:
                self.php_extensions.append(ext)

        self.runner_config.playbook = '{}.yml'.format(self.action)


    def _set_apache_vars(self):
        if self.action in ['wordpress', 'joomla']:
            if self.apache_document_root == DEFAULT_APACHE_DOCUMENT_ROOT:
                self.apache_document_root = '{}/{}'.format(
                    DEFAULT_APACHE_DOCUMENT_ROOT,
                    self.action
                )

            if self.apache_vhost_name == DEFAULT_APACHE_VHOST_NAME:
                self.apache_vhost_name = self.action

        elif self.action == 'drupal':
            if self.apache_document_root == DEFAULT_APACHE_DOCUMENT_ROOT:
                self.apache_document_root = '{}/drupal/web'.format(
                    DEFAULT_APACHE_DOCUMENT_ROOT
                )

            if self.apache_vhost_name == DEFAULT_APACHE_VHOST_NAME:
                self.apache_vhost_name = self.action

        elif self.action in ['laravel', 'suitecrm']:

            if self.action == 'suitecrm':
                self.app_name = 'suitecrm'

            if self.apache_document_root == DEFAULT_APACHE_DOCUMENT_ROOT:
                if self.action == 'suitecrm' and self.suitecrm_version == '7':
                    self.apache_document_root = '{}/{}'.format(
                        DEFAULT_APACHE_DOCUMENT_ROOT,
                        self.app_name
                    )
                else:
                    self.apache_document_root = '{}/{}/public'.format(
                        DEFAULT_APACHE_DOCUMENT_ROOT,
                        self.app_name
                    )

            if self.apache_vhost_name == DEFAULT_APACHE_VHOST_NAME:
                self.apache_vhost_name = self.app_name

        if FQDN(self.web_host).is_valid:
            server_name = self.web_host
        else:
            server_name = DEFAULT_APACHE_SERVER_NAME

        base_vhost_dict = {
            'base_vhost_file': '{}.conf'.format(DEFAULT_APACHE_VHOST_NAME),
            'document_root':  self.apache_document_root,
            'vhost_name':     self.apache_vhost_name,
            'server_name':    server_name,
            'server_admin':   self.apache_server_admin,
            'allow_override': self.get_apache_allow_override(),
        }

        self.apache_vhosts = [base_vhost_dict]

        if self.ssl_certbot:
            if not self.email_for_ssl:
                self.email_for_ssl = self.apache_server_admin
            if not self.domains_for_ssl:
                self.domains_for_ssl = [self.web_host]

        elif self.ssl_selfsigned:
            ssl_vhost_dict = deepcopy(base_vhost_dict)

            ssl_vhost_dict['base_vhost_file'] = 'default-ssl.conf'
            ssl_vhost_dict['vhost_name']      += '-ssl'

            self.apache_vhosts.append(ssl_vhost_dict)

            self.apache_custom_conf_name = 'ssl-params'

        # TODO: Do this conditionally, only for actions where we need it?
        if not self.composer_working_directory:
            self.composer_working_directory = self.apache_document_root


    def get_apache_allow_override(self):
        return (
            self.action in ['laravel', 'drupal']
            or (
                self.action == 'wordpress'
                # TODO: Deprecate this.
                and not self.wordpress_insecure_allow_xmlrpc
            )
            or (
                self.action == 'suitecrm'
                and self.suitecrm_version == '8'
            )
        )


    def print_banner(self):
        print(self.banner)


    def _init_inventory(self):
        self.private_data_helper.add_inventory_groups([
            'web_servers',
            'database_servers',
        ])
        self.private_data_helper.add_inventory_host(self.web_host, 'web_servers')
        self.private_data_helper.add_inventory_host(self.database_system_host,
                'database_servers')
        self.private_data_helper.set_inventory_ansible_user(self.web_host, self.web_user)
        self.private_data_helper.set_inventory_ansible_user(
                self.database_system_host, self.database_system_user)
        self.private_data_helper.write_inventory()


    def _update_env(self):
        extravars = [
            'web_host',
            'apache_vhosts',
            'apache_vhost_name',
            'apache_document_root',
            'apache_server_admin',
            'apache_custom_conf_name',
            # TODO: Ansible Runner has a dedicated feature for dealing
            # with passwords. Likely we'll have to implement support
            # for that in ansible-directory-helper.
            # For the time being, however, treat it as an extravar.
            'database_root_password',
            'database_username',
            'database_password',
            'database_name',
            'database_host',
            'database_table_prefix',
            'php_version',
            'php_packages_extra',
            'php_memory_limit',
            'php_upload_max_filesize',
            'php_post_max_size',
            'php_max_execution_time',
            'php_max_input_time',
            'php_max_file_uploads',
            'php_allow_url_fopen',
            'php_error_reporting',
            'php_display_errors',
            'composer_packages',
            'composer_project',
            'composer_working_directory',
            'site_title',
            'admin_username',
            'admin_password',
            'admin_email',
        ]

        if self.action == 'wordpress':
            extravars.extend([
                'wordpress_version',
                'wordpress_locale',
                'wordpress_url',
                'wordpress_insecure_allow_xmlrpc',
            ])
        elif self.action == 'joomla':
            extravars.extend([
                'joomla_version',
                'joomla_admin_full_name',
            ])
        elif self.action == 'drupal':
            extravars.extend([
                'drupal_profile',
            ])
        elif self.action == 'laravel':
            extravars.extend([
                'app_name',
                'app_build_path',
                'app_source_root',
                'laravel_artisan_commands',
                'app_local_env',
            ])
        elif self.action == 'suitecrm':
            extravars.extend([
                'app_source_root',
                'app_local_env',
                'suitecrm_version',
                'suitecrm_build_url',
                'suitecrm_demo_data',
            ])

        extravars.extend([
            'ssl_certbot',
            'email_for_ssl',
            'certbot_domains_string',
            'ssl_test_cert',
            'ssl_selfsigned',
            'extra_packages',
            'extra_env_vars',
            # TODO: This one especially... use Ansible Runner's
            # dedicated password feature, that is, we should add it
            # ansible-directory-helper.
            'ansible_sudo_pass',
            'open_database',
        ])

        for varname in extravars:
            if varname == 'server_name':
                if FQDN.is_valid(self.web_host):
                    value = self.web_host
                else:
                    value = DEFAULT_APACHE_SERVER_NAME

            elif varname == 'php_packages_extra':
                value = [
                    # TODO: This is a somewhat inelegant way to continue
                    # supporting 'php_version'. geerlingguy.php takes the
                    # variable 'php_default_version_debian', but it breaks
                    # if it receives an empty value, which in Lampsible, is
                    # most often the case.
                    # Support for php_version will be dropped in the next major
                    # version, and then the 'php{}' package can be removed.
                    'php{}'.format(
                        '' if self.php_version is None else self.php_version
                    ),
                    'libapache2-mod-php'
                ] + self.php_extensions

            elif varname in ['php_allow_url_fopen', 'php_display_errors']:
                value = 'On' if getattr(self, varname) else 'Off'

            elif varname == 'wordpress_url':
                if not self.ssl_certbot or self.web_host[:4] == 'www.':
                    value = self.web_host
                else:
                    value = 'www.{}'.format(self.web_host)

                if value not in self.domains_for_ssl:
                    self.domains_for_ssl.append(value)

            elif varname == 'certbot_domains_string':
                value = '-d {}'.format(' -d '.join(self.domains_for_ssl))

            # This lets us pass extra_env_vars to Lampsible in the more sensible dictionary format,
            # while still using them in the more convenient list format.
            elif varname == 'extra_env_vars':
                value = [
                    '{}={}'.format(
                        key,
                        val
                    ) for key, val in self.extra_env_vars.items()
                ]

                # And this is to make sure that if we're installing a Laravel
                # app, we write the variables to the app's .env file, and not
                # Apache's envvars file.
                if self.action == 'laravel':
                    self.private_data_helper.set_extravar(
                        'laravel_extra_env_vars',
                        value
                    )
                    value = []

            elif varname == 'app_source_root':
                value = '{}/{}'.format(
                    DEFAULT_APACHE_DOCUMENT_ROOT,
                    self.app_name
                )

            elif varname == 'suitecrm_build_url':
                value = SUITECRM_BUILD_URLS[self.suitecrm_version]

            elif varname == 'ansible_sudo_pass':
                if self.remote_sudo_password:
                    value = self.remote_sudo_password
                else:
                    continue

            elif varname == 'open_database':
                if self.database_system_host is None \
                        or self.database_system_host == self.web_host:
                    value = False
                else:
                    value = True

            else:
                value = getattr(self, varname)

            self.private_data_helper.set_extravar(varname, value)

        self.private_data_helper.write_env()


    def _prepare_config(self):
        self.runner_config.prepare()


    def _ensure_galaxy_dependencies(self):
        required_collections = []
        required_roles = []
        tmp_collections = []
        tmp_roles = []

        with open(GALAXY_REQUIREMENTS_FILE, 'r') as stream:
            tmp_collections = safe_load(stream)['collections']
        with open(GALAXY_REQUIREMENTS_FILE, 'r') as stream:
            tmp_roles       = safe_load(stream)['roles']

        for tmp_dict in tmp_collections:
            required_collections.append(tmp_dict['name'])
        for tmp_dict in tmp_roles:
            required_roles.append(tmp_dict['name'])

        # TODO There might be a more elegant way to do this - Right now,
        # we're expecting required_collections to always be a tuple,
        # and searching for requirements in a big string, but yaml/dict
        # would be better.
        installed_collections = run_command(
            executable_cmd='ansible-galaxy',
            cmdline_args=[
                'collection',
                'list',
                '--collections-path',
                os.path.join(USER_HOME_DIR, '.ansible'),
            ],
            quiet=True
        )[0]
        installed_roles = run_command(
            executable_cmd='ansible-galaxy',
            cmdline_args=[
                'role',
                'list',
                '--roles-path',
                os.path.join(USER_HOME_DIR, '.ansible'),
            ],
            quiet=True
        )[0]

        missing_collections = []
        for required in required_collections:
            if required not in installed_collections:
                missing_collections.append(required)
        if len(missing_collections) == 0:
            result = 0
        else:
            result = self._install_galaxy_dependencies(
                missing_collections,
                'collection'
            )

        if result != 0:
            return result

        missing_roles = []
        for required in required_roles:
            if required not in installed_roles:
                missing_roles.append(required)
        if len(missing_roles) == 0:
            return 0
        else:
            return self._install_galaxy_dependencies(
                missing_roles,
                'role'
            )


    def _install_galaxy_dependencies(self, dependencies, dependency_type):
        plural = '{}s'.format(dependency_type)
        if not self.ansible_galaxy_ok:
            formatted_dependency_list = '\n- '.join(dependencies)

            if not self.interactive:
                print(dedent("""
The following Ansible Galaxy {} are missing,
and need to be installed into {}:\n- {}\n
Please set the attribute 'Lampsible.ansible_galaxy_ok=True'.
                """.format(
                    plural,
                    USER_HOME_DIR,
                    formatted_dependency_list
                )))
                return 1

            ok_to_install = input(dedent(
                """
I have to download and install the following
Ansible Galaxy {} into {}:\n- {}\nIs this OK (yes/no)?
                """).format(
                plural,
                os.path.join(USER_HOME_DIR, '.ansible/'),
                formatted_dependency_list
            )).lower()
            while ok_to_install != 'yes' and ok_to_install != 'no':
                ok_to_install = input("Please type 'yes' or 'no': ")

            if ok_to_install != 'yes':
                return 1

        print('\nInstalling Ansible Galaxy {} into {} ...'.format(
            plural,
            os.path.join(USER_HOME_DIR, '.ansible')
        ))
        run_command(
            executable_cmd='ansible-galaxy',
            cmdline_args=[dependency_type, 'install'] + dependencies,
        )
        print('\n... {} installed.'.format(plural))
        return 0


    # TODO: Do it this way?
    #def dump_ansible_facts(self):
    #    ansible_runner_run(
    #        private_data_dir=self.private_data_dir,
    #        host_pattern=self.web_host,
    #        module='setup',
    #        module_args='no_log=true'
    #    )


    def run(self):
        self._set_apache_vars()
        self._update_env()
        self._prepare_config()

        rc = 1
        try:
            assert self._ensure_galaxy_dependencies() == 0
            self.runner.run()
            print(self.runner.stats)
            rc = self.runner.rc
        except (AssertionError, RuntimeError):
            pass

        self.private_data_helper.cleanup_dir()
        return rc
