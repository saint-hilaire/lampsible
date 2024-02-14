from copy import copy
from warnings import warn
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

    def handle_defaults(
        self,
        default_args,
        set_vals=True,
        print_warnings=False
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

        set_vals -- Optional. If True, set the values of the args passed in.
                    Defaults to True. Set it to False if you only want to warn
                    the user about default arguments (like insecure database
                    credentials), without setting the default values
                    (assuming that the defaults were set by argparse itself
                    in the main method).

        print_warnings -- Optional. If True, print a warning if we get a
                          default value. Default value is False.
        """
        for arg_dict in default_args:
            try:
                default_value = arg_dict['override_default_value']
            except KeyError:
                default_value = arg_dict['cli_default_value']
            user_value = getattr(self.args, arg_dict['arg_name'])

            if user_value == arg_dict['cli_default_value']:
                if set_vals:
                    setattr(
                        self.args,
                        arg_dict['arg_name'],
                        default_value
                    )
                if print_warnings:
                    warn('WARNING! Got no ' \
                        + self.var_name_to_cli_arg(arg_dict['arg_name']) \
                        + '. Defaulting to ' + default_value)


    def var_name_to_cli_arg(self, var_name):
        return '--{}'.format(var_name.replace('_', '-'))


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
        #     self.handle_defaults([{
        #         'arg_name': 'email_for_ssl',
        #         'cli_default_value': self.args.apache_server_admin,
        #     }], False, True)


    def validate_database_args(self):

        if self.args.database_engine != DEFAULT_DATABASE_ENGINE \
            or self.args.database_host != DEFAULT_DATABASE_HOST \
            or self.args.php_my_admin:

            raise NotImplementedError()

        if self.args.action == 'wordpress':
            self.handle_defaults([
                {
                    'arg_name': 'database_name',
                    'cli_default_value': DEFAULT_DATABASE_NAME,
                    'override_default_value': 'wordpress',
                },
                {
                    'arg_name': 'database_table_prefix',
                    'cli_default_value': DEFAULT_DATABASE_TABLE_PREFIX,
                    'override_default_value': 'wp_',
                }
            ], True, True)

        self.handle_defaults([
            {
                'arg_name': 'database_username',
                'cli_default_value': DEFAULT_DATABASE_USERNAME,
            },
            {
                'arg_name': 'database_password',
                'cli_default_value': DEFAULT_DATABASE_PASSWORD,
            },
        ], False, True)


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


    def validate_args(self):
        self.validate_apache_args()
        self.validate_database_args()
        self.validate_ssl_args()
        self.validate_php_args()
