from copy import copy
from secrets import token_hex
from warnings import warn
from getpass import getpass
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
    def get_domain_for_wordpress(self):
        try:
            return self.domain_for_wordpress
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
                print('The value you passed for {} is too short! I will automatically generate a value for you, and use that. If in doubt, you should leave this argument blank, to use automatically generated values. See the file wp-config.php on your server.'.format(
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
                    print('Using {} value \'{}\'.'.format(
                        self.var_name_to_cli_arg(arg_dict['arg_name']),
                        default_value
                    ))


    def var_name_to_cli_arg(self, var_name):
        return '--{}'.format(var_name.replace('_', '-'))


    def get_pass_and_check(self, prompt, min_length):
        password = getpass(prompt)
        while len(password) < min_length:
            password = getpass('That password is too short. Please enter another password: ')
        double_check = getpass('Please retype password: ')
        if password == double_check:
            return password
        else:
            print('Passwords don\'t match. Please try again.')
            return self.get_pass_and_check(prompt, min_length)


    def validate_apache_args(self):

        base_vhost_dict = {
            'base_vhost_file': '{}.conf'.format(DEFAULT_APACHE_VHOST_NAME),
            'document_root':  self.args.apache_document_root,
            'vhost_name':     self.args.apache_vhost_name,
            # TODO: Temporarily disabled because it does not play
            # nicely with Certbot.
            # 'server_name':    self.args.apache_server_name,
            'server_admin':   self.args.apache_server_admin,
        }

        if self.args.action == 'wordpress':

            if self.args.apache_document_root == DEFAULT_APACHE_DOCUMENT_ROOT:
                base_vhost_dict['document_root'] = '{}/wordpress'.format(
                    DEFAULT_APACHE_DOCUMENT_ROOT)
            if self.args.apache_vhost_name == DEFAULT_APACHE_VHOST_NAME:
                base_vhost_dict['vhost_name'] = 'wordpress'

        self.apache_vhosts = [base_vhost_dict]

        if self.args.ssl_selfsigned or self.args.ssl_certbot:

            ssl_vhost_dict = copy(base_vhost_dict)

            ssl_vhost_dict['base_vhost_file'] = 'default-ssl.conf'
            ssl_vhost_dict['vhost_name']      += '-ssl'

            self.apache_vhosts.append(ssl_vhost_dict)
            self.apache_custom_conf_name = 'ssl-params'

        # if ssl_action:
        #     # TODO: Does not work for Certbot, unless the client is
        #     # run with the flag --register-unsafely-without-email.
        #     # TODO: This method has been refactored, so this is now broken.
        #     self.handle_defaults([{
        #         'arg_name': 'email_for_ssl',
        #         'cli_default_value': self.args.apache_server_admin,
        #     }], False, True)


    def validate_database_args(self):

        # TODO: Sanity check database username and database name.

        if self.args.database_engine != DEFAULT_DATABASE_ENGINE \
            or self.args.database_host != DEFAULT_DATABASE_HOST \
            or self.args.php_my_admin:

            raise NotImplementedError()

        if self.args.database_password \
            and not self.args.insecure_cli_password:

            exit('It\'s insecure to pass passwords via CLI args! If you are sure that you want to do this, rerun this command with the --insecure-cli-password flag.')

        # TODO: Add some option like --wordpress-defaults, to improve user
        # experience. Otherwise, the user would always be asked about defaulting
        # to 'wordpress' and 'wp_' for database name and table prefix, which
        # might be a little annoying.
        if self.args.action == 'wordpress':
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
            ], True, True)

        if self.args.database_username and not self.args.database_password:
            self.args.database_password = self.get_pass_and_check(
                'Please enter a database password: ',
                7
            )


    def validate_ssl_args(self):

        if self.args.ssl_certbot:
            if self.args.ssl_selfsigned:
                warn('Warning: Got --ssl-certbot, but also got --ssl-selfsigned. Ignoring --ssl-selfsigned and using --ssl-certbot.')
            ssl_action = 'certbot'
        elif self.args.ssl_selfsigned:
            warn('Warning! Creating a self signed certificate to handle the site\'s encryption. This is less secure and will appear untrustworthy to any visitors. Only use this for testing environments.')
            ssl_action = 'selfsigned'
        else:
            warn('WARNING! Your site will not have any encryption enabled! This is very insecure, as passwords and other sensitive data will be transmitted in clear text. DO NOT use this on any remote host or over any partially untrusted network. ONLY use this for local, secure, private and trusted networks, ideally only for local development servers.')
            ssl_action = None

        # TODO: Improve this when we fix Certbot.
        if ssl_action == 'certbot':
            self.handle_defaults([
                {
                    'arg_name': 'domains_for_ssl',
                    'cli_default_value': None,
                    'override_default_value': self.args.hosts.split(','),
                },
                {
                    'arg_name': 'email_for_ssl',
                    'cli_default_value': self.args.apache_server_admin,
                },
            ])
            if self.args.action == 'wordpress':
                self.args.domains_for_ssl.append(
                    'www.{}'.format(self.args.domains_for_ssl[0])
                )
                self.domain_for_wordpress = self.args.domains_for_ssl[-1]


    def validate_php_args(self):
        # TODO: If we can get the ansible_facts back into a Python variable,
        # we can validate this stuff too.
        # NOTE:
        # * Ubuntu versions 20 and older do not support PHP versions 8.0 or newer
        # * Ubuntu 22 does not support PHP 8.0. PHP 8.1 is supported.
        # To work around the above points, you would have to manually configure the
        # APT repository.
        if self.args.skip_php_extensions:
            warn('Will not install common PHP extensions. WordPress, Laravel, and other common CMS or frameworks will probably not work.')


    def print_warnings(self):
        if self.args.insecure_skip_fail2ban:
            print('Warning! Will not install fail2ban! Your site will potentially be vulnerable to various brute force attacks. You should only pass the \'--insecure-skip-fail2ban\' flag if you have a good reason to do so. On production servers, always install fail2ban!')
        if self.args.wordpress_insecure_allow_xmlrpc:
            print('Warning! Your WordPress site\'s xmlrpc.php endpoint will be enabled - this is insecure! The endpoint xmlrpc.php is a feature from older WordPress versions which allowed programmatic access to the WordPress backend. Although it has numerous known security vulnerabilities, namely a brute force and a DoS vulnerability, it is still, for some reason, enabled by default in current WordPress versions. Lampsible will, by default, block this endpoint with an .htaccess configuration, unless you specify otherwise, which you just did. You should not be doing this, unless you have some good reason to do so!')


    def validate_args(self):
        self.validate_apache_args()
        self.validate_database_args()
        self.validate_ssl_args()
        self.validate_php_args()
        self.print_warnings()
