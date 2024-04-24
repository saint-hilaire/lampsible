from re import match
from copy import copy
from secrets import token_hex
from warnings import warn
from getpass import getpass
from requests import head as requests_head
from fqdn import FQDN
from lampsible.constants import *


class ArgValidator():

    def __init__(self, args):
        self.args = args


    def get_args(self):
        return self.args


    def get_apache_vhosts(self):
        return self.apache_vhosts


    # TODO: I don't find this very elegant.
    def get_apache_custom_conf_name(self):
        try:
            return self.apache_custom_conf_name
        except AttributeError:
            return ''


    # TODO: Improve/remove this when we fix Certbot.
    def get_wordpress_url(self):
        try:
            return self.wordpress_url
        except AttributeError:
            return ''


    def get_wordpress_auth_vars(self):
        auth_var_names = [
            'auth_key',
            'secure_auth_key',
            'logged_in_key',
            'nonce_key',
            'auth_salt',
            'secure_auth_salt',
            'logged_in_salt',
            'nonce_salt',
        ]
        auth_vars = {}

        for var in auth_var_names:
            must_generate = False
            warn_user     = False

            if not getattr(self.args, 'wordpress_{}'.format(var)):
                must_generate = True
            elif len(getattr(self.args, 'wordpress_{}'.format(var))) < 32:
                must_generate = True
                warn_user     = True

            if must_generate:
                auth_vars[var.upper()] = token_hex(64)
            else:
                auth_vars[var.upper()] = getattr(
                    self.args,
                    'wordpress_{}'.format(var)
                )

            if warn_user:
                print('\nThe value you passed for {} is too short! I will automatically generate a value for you, and use that. If in doubt, you should leave this argument blank, to use automatically generated values. See the file wp-config.php on your server.'.format(
                    self.var_name_to_cli_arg('wordpress_{}'.format(var))
                ))

        return auth_vars


    def get_apache_allow_override(self):
        return (
            self.args.action == 'laravel'
            or (
                self.args.action == 'wordpress'
                and not self.args.wordpress_insecure_allow_xmlrpc
            )
        )


    def get_certbot_domains_string(self):
        try:
            return '-d {}'.format(' -d '.join(self.args.domains_for_ssl))
        except TypeError:
            return ''


    def get_certbot_test_cert_string(self):
        return '--test-cert' if self.args.test_cert else ''


    def get_extravars_dict(self):
        extravars = {
            'apache_vhosts': self.get_apache_vhosts(),
            'apache_custom_conf_name': self.get_apache_custom_conf_name(),
            'database_username': self.args.database_username,
            'database_password': self.args.database_password,
            'database_host': self.args.database_host,
            'database_name': self.args.database_name,
            'database_table_prefix': self.args.database_table_prefix,
            'php_version': self.args.php_version,
            'skip_php_extensions': self.args.skip_php_extensions,
            'ssl_certbot': self.args.ssl_certbot,
            'ssl_selfsigned': self.args.ssl_selfsigned,
            'email_for_ssl': self.args.email_for_ssl,
            'certbot_domains_string': self.get_certbot_domains_string(),
            'certbot_test_cert_string': self.get_certbot_test_cert_string(),
            'insecure_skip_fail2ban': self.args.insecure_skip_fail2ban,
        }
        if self.args.remote_sudo_password:
            # TODO: It would be better to not include this as an extravar, but to
            # make use of Ansible Runner's password feature in the
            # Input Directory Hierarchy.
            extravars['ansible_sudo_pass'] = self.args.remote_sudo_password

        if self.args.action == 'wordpress':
            extravars['wordpress_version'] = self.args.wordpress_version
            extravars['wordpress_locale'] = self.args.wordpress_locale
            extravars['wordpress_site_title'] = self.args.wordpress_site_title
            extravars['wordpress_admin_username'] = \
                self.args.wordpress_admin_username
            extravars['wordpress_admin_password'] = \
                self.args.wordpress_admin_password
            extravars['wordpress_admin_email'] = \
                self.args.wordpress_admin_email

            # TODO: This should be deprecated in favor of
            # letting WP-CLI handlethese.
            extravars['wordpress_auth_vars'] = self.get_wordpress_auth_vars()

            extravars['wordpress_insecure_allow_xmlrpc'] = \
                self.args.wordpress_insecure_allow_xmlrpc
            extravars['wordpress_url'] = self.get_wordpress_url()
            extravars['wp_apache_document_root'] = self.wp_apache_document_root
            extravars['wordpress_manual_install'] = \
                self.args.wordpress_manual_install

        return extravars


    def handle_defaults(
        self,
        default_args,
        ask_user=False,
        verbose=False
    ):
        """Handles defaults in various cases, optionally setting values with
        application wide defaults or overriding values, and optionally
        printing warnings.

        Positional arguments

        default_args -- A list of dictionaries, which defines the arguments,
                        and how to treat them. The following dictionary serves
                        as an example:
            {
                # required
                'arg_name': 'some_cli_arg', # The user passed this in as
                                            # --some-cli-arg - We also have a
                                            # helper function to get the arg
                                            # name in that format.
                # required
                'cli_default_value': DEFAULT_ARG_VALUE,
                # optional
                'override_default_value': 'some use case specific default',
            }

        ask_user -- Optional. If True, then if we got default values,
                    prompt the user to input their own value,
                    and if they leave it blank,
                    fall back to default values. Defaults to False.

        verbose --  Optional. If True, then if we are using some
                    default value, warn the user about this. This is useful
                    for credentials, in case we're falling back to some
                    insecure value.
        """
        for arg_dict in default_args:
            try:
                default_value = arg_dict['override_default_value']
            except KeyError:
                default_value = arg_dict['cli_default_value']
            user_value = getattr(self.args, arg_dict['arg_name'])

            if user_value == arg_dict['cli_default_value']:
                if ask_user:
                    tmp_val = input(
                        'Got no {}. Please enter a value now, or leave blank to default to \'{}\': '.format(

                            self.var_name_to_cli_arg(arg_dict['arg_name']),
                            default_value
                        )
                    )
                    if tmp_val == '':
                        tmp_val = default_value
                    default_value = tmp_val

                setattr(
                    self.args,
                    arg_dict['arg_name'],
                    default_value
                )

                if verbose:
                    print('\nUsing {} value \'{}\'.'.format(
                        self.var_name_to_cli_arg(arg_dict['arg_name']),
                        default_value
                    ))


    def var_name_to_cli_arg(self, var_name):
        return '--{}'.format(var_name.replace('_', '-'))


    def get_pass_and_check(self, prompt, min_length=0, confirm=False):
        password = getpass(prompt)
        while min_length > 0 and len(password) < min_length:
            password = getpass('That password is too short. Please enter another password: ')
        if confirm:
            double_check = getpass('Please retype password: ')
            if password == double_check:
                return password
            else:
                print('\nPasswords don\'t match. Please try again.')
                return self.get_pass_and_check(prompt, min_length, True)
        else:
            return password


    def validate_ansible_runner_args(self):
        user_at_host = self.args.user_at_host.split('@')
        try:
            self.web_host_user = user_at_host[0]
            self.web_host      = user_at_host[1]
        except IndexError:
            print('FATAL! First positional argument must be in the format of \'user@host\'')
            return 1

        if self.args.remote_sudo_password \
            and not self.args.insecure_cli_password:
            print(INSECURE_CLI_PASS_WARNING)
            return 1
        if self.args.ask_remote_sudo:
            self.args.remote_sudo_password = self.get_pass_and_check(
                'Please enter sudo password for remote host: ')
        return 0


    def validate_apache_args(self):

        server_name = self.web_host
        try:
            assert FQDN(server_name).is_valid
        except AssertionError:
            server_name = DEFAULT_APACHE_SERVER_NAME

        base_vhost_dict = {
            'base_vhost_file': '{}.conf'.format(DEFAULT_APACHE_VHOST_NAME),
            'document_root':  self.args.apache_document_root,
            'vhost_name':     self.args.apache_vhost_name,
            'server_name':    server_name,
            'server_admin':   self.args.apache_server_admin,
            'allow_override': self.get_apache_allow_override(),
        }

        self.apache_vhosts = [base_vhost_dict]

        if self.args.ssl_selfsigned:

            ssl_vhost_dict = copy(base_vhost_dict)

            ssl_vhost_dict['base_vhost_file'] = 'default-ssl.conf'
            ssl_vhost_dict['vhost_name']      += '-ssl'

            self.apache_vhosts.append(ssl_vhost_dict)

            if self.args.ssl_selfsigned:
                self.apache_custom_conf_name = 'ssl-params'

        return 0


    def validate_database_args(self):

        # TODO: Sanity check database username and database name.

        if self.args.database_engine != DEFAULT_DATABASE_ENGINE \
            or self.args.database_host != DEFAULT_DATABASE_HOST \
            or self.args.php_my_admin:

            raise NotImplementedError()

        if self.args.database_password \
            and not self.args.insecure_cli_password:

            print(INSECURE_CLI_PASS_WARNING)
            return 1

        if self.args.database_username and not self.args.database_password:
            self.args.database_password = self.get_pass_and_check(
                'Please enter a database password: ',
                0,
                True
            )

        return 0


    def validate_ssl_args(self):

        if self.args.ssl_certbot:
            ssl_action = 'certbot'
        elif self.args.ssl_selfsigned:
            ssl_action = 'selfsigned'
        else:
            ssl_action = None

        if ssl_action == 'certbot':
            self.handle_defaults([
                {
                    'arg_name': 'domains_for_ssl',
                    'cli_default_value': None,
                    'override_default_value': [self.web_host],
                },
                {
                    'arg_name': 'email_for_ssl',
                    'cli_default_value': None,
                    'override_default_value': self.args.apache_server_admin,
                },
            ])

            if not match(r"[^@]+@[^@]+\.[^@]+", self.args.email_for_ssl):
                print("\nFATAL! --email-for-ssl needs to be valid. Got '{}'. Aborting.".format(
                    self.args.email_for_ssl))
                return 1

        return 0


    def validate_php_args(self):
        # TODO: If we can get the ansible_facts back into a Python variable,
        # we can validate this stuff too.
        # NOTE:
        # * Ubuntu versions 20 and older do not support PHP versions 8.0 or newer
        # * Ubuntu 22 does not support PHP 8.0. PHP 8.1 is supported.
        # To work around the above points, you would have to manually configure the
        # APT repository.
        if self.args.skip_php_extensions:
            print('\nWill not install common PHP extensions. WordPress, Laravel, and other common CMS or frameworks will probably not work.')

        return 0


    def validate_wordpress_args(self):
        if self.args.action != 'wordpress':
            return 0

        if not self.is_valid_wordpress_version(self.args.wordpress_version):
            print('\nInvalid WordPress version! Leave --wordpress-version blank to default to \'{}\''.format(DEFAULT_WORDPRESS_VERSION))
            return 1

        if self.args.apache_document_root == DEFAULT_APACHE_DOCUMENT_ROOT:
            wp_apache_document_root = '{}/wordpress'.format(
                DEFAULT_APACHE_DOCUMENT_ROOT
            )
        else:
            wp_apache_document_root = self.args.apache_document_root

        if self.args.apache_vhost_name == DEFAULT_APACHE_VHOST_NAME:
            wp_apache_vhost_name = 'wordpress'
        else:
            wp_apache_vhost_name = self.args.apache_vhost_name

        for i in range(len(self.apache_vhosts)):
            self.apache_vhosts[i]['document_root'] = wp_apache_document_root
            self.apache_vhosts[i]['vhost_name'] = wp_apache_vhost_name

        # NOTE: We might need to access this in other scenarios, not just
        # for WordPress, but for now, only WordPress.
        # The Apache DocumentRoot is defined individually for each vhost,
        # and there can be several of those.
        self.wp_apache_document_root = wp_apache_document_root

        self.handle_defaults([
            {
                'arg_name': 'database_name',
                'cli_default_value': None,
                'override_default_value': 'wordpress',
            },
            {
                'arg_name': 'database_username',
                'cli_default_value': None,
                'override_default_value': DEFAULT_DATABASE_USERNAME,
            },
            {
                'arg_name': 'database_table_prefix',
                'cli_default_value': DEFAULT_DATABASE_TABLE_PREFIX,
                'override_default_value': 'wp_',
            },
            {
                'arg_name': 'wordpress_site_title',
                'cli_default_value': None,
                'override_default_value': DEFAULT_WORDPRESS_SITE_TITLE,
            },
            {
                'arg_name': 'wordpress_admin_username',
                'cli_default_value': None,
                'override_default_value': DEFAULT_WORDPRESS_ADMIN_USERNAME,
            },
            {
                'arg_name': 'wordpress_admin_email',
                'cli_default_value': None,
                'override_default_value': DEFAULT_WORDPRESS_ADMIN_EMAIL,
            },
        ], True, True)

        self.validate_database_args()

        if self.args.wordpress_admin_password \
            and not self.args.insecure_cli_password:
            print(INSECURE_CLI_PASS_WARNING)
            return 1

        if not self.args.wordpress_admin_password:
            self.args.wordpress_admin_password = self.get_pass_and_check(
                'Please choose a password for the WordPress admin: ',
                0,
                True
            )

        if self.args.ssl_certbot:
            if self.web_host[:4] == 'www.':
                www_domain = self.web_host
            else:
                www_domain = 'www.{}'.format(self.web_host)

            if www_domain not in self.args.domains_for_ssl:
                self.args.domains_for_ssl.append(www_domain)

            self.wordpress_url = www_domain

        else:
            self.wordpress_url = self.web_host

        return 0


    def is_valid_wordpress_version(self, wp_version):
        recent_versions = [
            'latest',
            'nightly',
            '6.5.2',
            '6.5',
            '6.4.4',
            '6.4.3',
            '6.4.2',
            '6.4.1',
            '6.4',
        ]
        if wp_version in recent_versions:
            return True

        try:
            r = requests_head(
                'https://wordpress.org/wordpress-{}.tar.gz'.format(wp_version)
            )
            assert r.status_code == 200
            return True
        except AssertionError:
            return False


    def print_warnings(self):
        if self.args.insecure_skip_fail2ban:
            print('\nWarning! Will not install fail2ban! Your site will potentially be vulnerable to various brute force attacks. You should only pass the \'--insecure-skip-fail2ban\' flag if you have a good reason to do so. On production servers, always install fail2ban!')

        if self.args.wordpress_insecure_allow_xmlrpc:
            print('\nWarning! Your WordPress site\'s xmlrpc.php endpoint will be enabled - this is insecure! The endpoint xmlrpc.php is a feature from older WordPress versions which allowed programmatic access to the WordPress backend. Although it has numerous known security vulnerabilities, namely a brute force and a DoS vulnerability, it is still, for some reason, enabled by default in current WordPress versions. Lampsible will, by default, block this endpoint with an .htaccess configuration, unless you specify otherwise, which you just did. You should not be doing this, unless you have some good reason to do so!')

        if self.args.ssl_certbot and self.args.ssl_selfsigned:
            print('\nWarning: Got --ssl-certbot, but also got --ssl-selfsigned. Ignoring --ssl-selfsigned and using --ssl-certbot.')
        elif self.args.ssl_selfsigned:
            print('\nWarning! Creating a self signed certificate to handle the site\'s encryption. This is less secure and will appear untrustworthy to any visitors. Only use this for testing environments.')
        elif not (self.args.ssl_selfsigned or self.args.ssl_certbot):
            print('\nWARNING! Your site will not have any encryption enabled! This is very insecure, as passwords and other sensitive data will be transmitted in clear text. DO NOT use this on any remote host or over any partially untrusted network. ONLY use this for local, secure, private and trusted networks, ideally only for local development servers.')


    def validate_args(self):
        validate_methods = [
            'validate_ansible_runner_args',
            'validate_apache_args',
            'validate_database_args',
            'validate_ssl_args',
            'validate_php_args',
            'validate_wordpress_args',
        ]
        for method_name in validate_methods:
            method = getattr(self, method_name)
            result = method()
            if result != 0:
                return result

        self.print_warnings()
        return 0
