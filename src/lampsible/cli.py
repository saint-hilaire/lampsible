import argparse
from textwrap import dedent
from ansible_runner import Runner, RunnerConfig, run_command
from . import __version__
from .constants import *
from .lampsible import Lampsible
from .arg_validator import ArgValidator


def main():

    parser = argparse.ArgumentParser(
        prog='lampsible',
        description='LAMP Stacks with Ansible',
    )

    # ----------------------
    #                      -
    #  Required arguments  -
    #                      -
    # ----------------------

    parser.add_argument('web_user_host', nargs='?',
        help="example: someuser@somehost.com"
    )
    parser.add_argument('action', choices=SUPPORTED_ACTIONS, nargs='?')

    # ----------------------
    #                      -
    #  Basic Options       -
    #                      -
    # ----------------------

    # Ansible Runner
    # --------------
    parser.add_argument('--ask-remote-sudo', action='store_true',
        help="""
        Pass this flag if you want to be prompted for the sudo password
        of the remote server.
        """
    )

    # Apache
    # ------
    parser.add_argument('-a', '--apache-server-admin',
        default=DEFAULT_APACHE_SERVER_ADMIN,
        help="""
        the email address of the server administrator,
        which is passed to Apache's 'ServerAdmin' configuration.
        Defaults to '{}' but if you should pass in a real email address.
        """.format(DEFAULT_APACHE_SERVER_ADMIN)
    )

    # Database
    # --------
    parser.add_argument('-d', '--database-username',
        help="""
        database user - If your website requires a database,
        and you leave this blank, you will be prompted to enter a value,
        or default to '{}'.
        If no database is required, and you leave this blank,
        no database user will be created.
        """.format(DEFAULT_DATABASE_USERNAME)
    )
    parser.add_argument('-n', '--database-name',
        help="""
        name of your database - If your website requires a database,
        and you leave this blank, you will be prompted to enter a value,
        or default to a sensible default,
        depending on your app.
        If no database is required, and you leave this blank,
        no database will be created.
        """
    )
    parser.add_argument('--database-host', default=DEFAULT_DATABASE_HOST)
    parser.add_argument('--database-system-user-host',
        help="""
        If database server is different than web server,
        pass this, and Ansible will install database stuff here.
        Otherwise, leave blank, and Ansible will install database
        stuff on web server, like in v1.
        """
    )
    # TODO: In the next major version, ask for database root password by default,
    # and offer a new flag to skip this - like '--no-database-root-password'.
    parser.add_argument('--ask-database-root-password', action='store_true',
        help="""
        Pass this flag to be prompted for the database root password.
        In a future version, you will be asked for the database root password
        by default.
        """
    )
    # TODO
    # parser.add_argument('--database-engine', default=DEFAULT_DATABASE_ENGINE)

    # PHP
    # ---
    parser.add_argument('-p', '--php-version', default=DEFAULT_PHP_VERSION,
        help="""
        Deprecated. This flag will be dropped in v3.
        the version of PHP to be installed, defaults to '{}'.
        Leave it blank to let Lampsible pick the right version
        based on your remote server
        """.format(DEFAULT_PHP_VERSION)
    )
    # TODO
    # parser.add_argument('--php-my-admin', action='store_true')

    # All CMS
    # -------
    parser.add_argument('--site-title', '-t',
        help="""
        The "Site Title" configuration of your website.
        If you leave this blank, you will be prompted to enter a value,
        or default to '{}'
        """.format(DEFAULT_SITE_TITLE)
    )
    parser.add_argument('--admin-username',
        help="""
        The admin username of your website.
        If you leave this blank, you will be prompted to enter a value,
        or default to '{}'
        """.format(DEFAULT_ADMIN_USERNAME)
    )
    parser.add_argument('--admin-email',
        help="""
        The email address of your website's admin username.
        If you leave this blank, you will be prompted to enter a value,
        or default to '{}'
        """.format(DEFAULT_ADMIN_EMAIL)
    )

    # WordPress
    # ---------
    parser.add_argument('-w', '--wordpress-version',
        default=DEFAULT_WORDPRESS_VERSION,
        help="""
        the version of WordPress to be installed, defaults to '{}'
        """.format(DEFAULT_WORDPRESS_VERSION)
    )
    parser.add_argument('--wordpress-locale',
        default=DEFAULT_WORDPRESS_LOCALE,
        help="the locale of your WordPress site, defaults to '{}'".format(
            DEFAULT_WORDPRESS_LOCALE
        )
    )

    # Joomla
    # ------

    parser.add_argument('--joomla-version', '-j',
        default=DEFAULT_JOOMLA_VERSION)
    parser.add_argument('--joomla-admin-full-name', '-J')

    # Drupal
    # ------

    parser.add_argument('--drupal-profile', choices=AVAILABLE_DRUPAL_PROFILES,
        default=DEFAULT_DRUPAL_PROFILE,
            help="""
            Drupal supports various "profiles".
            Out of the box, these are available: {}.
            Defaults to {}
            """.format(
                ', '.join(AVAILABLE_DRUPAL_PROFILES),
                DEFAULT_DRUPAL_PROFILE)
    )

    # Web applications
    # ----------------
    parser.add_argument('--app-name', default='laravel-app',
        help="""
        the name of your Laravel app, if you're installing one.
        Leave blank to default to 'laravel-app'
        """
    )
    parser.add_argument('--app-build-path',
        help="""
        If you are installing a Laravel app,
        use this option to specify the local path of a production ready
        build-archive of your app,
        for example /path/to/some-app-2.0.tar.gz
        """
    )
    parser.add_argument('--suitecrm-version',
        choices=SUPPORTED_SUITECRM_VERSIONS,
        default=DEFAULT_SUITECRM_VERSION,
        help="""
        If installing SuiteCRM, this is the version that will be installed.
        Default value is '{}', and this the the preferred version.
        Available choices are: {}.
        """.format(
            DEFAULT_SUITECRM_VERSION,
            "'" + "', '".join(SUPPORTED_SUITECRM_VERSIONS) + "'"
        )
    )
    parser.add_argument('--suitecrm-demo-data', action='store_true',
        help="""
        If installing SuiteCRM, pass this flag to populate your
        installation with some demo data. This is a feature supplied by
        SuiteCRM, and works in version 8 or newer.
        """
    )

    # SSL
    # ---
    parser.add_argument('--ssl-test-cert', action='store_true',
        help="""
        Set this flag to run certbot with the '--test-cert' flag.
        This is useful if you frequently set up a test server,
        and need to avoid being rate limited by Let's Encrypt.
        """
    )
    parser.add_argument('--ssl-selfsigned', action='store_true',
        help="""
        Pass this flag to generate a self signed SSL certificate for your site.
        You should only do this on test servers,
        because it makes your site look untrustworthy to visitors.
        """
    )
    parser.add_argument('--email-for-ssl',
        help="""
        the email address that will be passed to Certbot.
        If left blank, the value of '--apache-server-admin'
        will be used instead.
        """
    )
    parser.add_argument('--domains-for-ssl',
        help="""
        a comma separated list of domains that will be passed to Certbot.
        If left blank, Lampsible will figure out what to use
        based on your host and action.
        """
    )
    parser.add_argument('--insecure-no-ssl', action='store_true',
        help="""
        Pass this flag to set up your website without any SSL encryption.
        This is insecure, and should only be done on test servers in
        local networks.
        """
    )

    # ----------------------
    #                      -
    #  Advanced Options    -
    #                      -
    # ----------------------

    # Ansible Runner
    # --------------
    parser.add_argument('--remote-sudo-password',
        help="""
        sudo password of the remote server,
        this only works if you also pass '--insecure-cli-password'.
        This is not recommended, you should use '--ask-remote-sudo' instead.
        """
    )
    parser.add_argument('--ssh-key-file', '-i',  help='path to your private SSH key')
    parser.add_argument('--private-data-dir',
        default=DEFAULT_PRIVATE_DATA_DIR,
        help="""
        the "private data directory" that Ansible Runner will use.
        Default is '{}'. You can use this flag to pass an alternative value.
        However, it's best to just leave this blank.
        Be advised that Ansible Runner will write sensitive data here,
        like your private SSH key and passwords,
        but Lampsible will delete this directory when it finishes.
        """
    )
    parser.add_argument('--ansible-galaxy-ok', action='store_true',
        help="""
        Pass this flag to give your consent to install any missing
        Ansible Galaxy dependencies onto your local machine.
        Otherwise, if any Galaxy Collections are missing, you will be asked
        if it is OK to install them.
        """
    )

    # Apache
    # ------
    parser.add_argument('--apache-vhost-name',
        default=DEFAULT_APACHE_VHOST_NAME,
        help="""
        the name of your site's Apache virtual host - leave this blank to
        let Lampsible pick a good default."
        """
    )
    parser.add_argument('--apache-document-root',
        default=DEFAULT_APACHE_DOCUMENT_ROOT,
        help="""
        your Apache virtual hosts' 'DocumentRoot' configuration - leave this
        blank to let Lampsible pick a good default.
        """
    )

    # Database
    # --------
    parser.add_argument('--database-password',
        help="""
        Use this flag to pass in the database password directly. This is
        not advised, and will only work if you also pass
        '--insecure-cli-password'. You should leave this blank instead,
        and Lampsible will prompt you for a password.
        """
    )
    parser.add_argument('--database-root-password',
        help="""
        Use this flag to pass in the database root password directly. This is
        not advised, and will only work if you also pass
        '--insecure-cli-password'. You should leave this blank instead,
        and Lampsible will prompt you for a password.
        """
    )
    parser.add_argument('--database-table-prefix',
        default=DEFAULT_DATABASE_TABLE_PREFIX,
        help="""
        prefix for your database tables, this is currently only used by
        WordPress, where it defaults to '{}'
        """.format(DEFAULT_DATABASE_TABLE_PREFIX)
    )

    # PHP
    # ---
    parser.add_argument('--php-extensions',
        help="""
        A comma separated list of PHP extensions to install.
        Do not prepend them with 'php-', so simply pass in something like
        '--php-extensions mysql,mbstring,gd', and Lampsible will install the
        proper packages.
        However, it's best to leave this blank, and let Lampsible pick
        sensible defaults depending on what you are installing, and only use
        this, if you have a specific use case that Lampsible's default
        behavior does not cover.
        """
    )
    parser.add_argument('--php-memory-limit',
        default=DEFAULT_PHP_MEMORY_LIMIT,
        help="""
        'memory_limit' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_MEMORY_LIMIT)
    )
    parser.add_argument('--php-upload-max-filesize',
        default=DEFAULT_PHP_UPLOAD_MAX_FILESIZE,
        help="""
        'upload_max_filesize' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_UPLOAD_MAX_FILESIZE)
    )
    parser.add_argument('--php-post-max-size',
        default=DEFAULT_PHP_POST_MAX_SIZE,
        help="""
        'post_max_size' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_POST_MAX_SIZE)
    )
    parser.add_argument('--php-max-execution-time',
        default=DEFAULT_PHP_MAX_EXECUTION_TIME,
        help="""
        'max_execution_time' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_MAX_EXECUTION_TIME)
    )
    parser.add_argument('--php-max-input-time',
        default=DEFAULT_PHP_MAX_INPUT_TIME,
        help="""
        'max_input_time' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_MAX_INPUT_TIME)
    )
    parser.add_argument('--php-max-file-uploads',
        default=DEFAULT_PHP_MAX_FILE_UPLOADS,
        help="""
        'max_file_uploads' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_MAX_FILE_UPLOADS)
    )
    parser.add_argument('--php-allow-url-fopen',
        default=DEFAULT_PHP_ALLOW_URL_FOPEN,
        help="""
        'allow_url_fopen' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_ALLOW_URL_FOPEN)
    )
    parser.add_argument('--php-error-reporting',
        default=DEFAULT_PHP_ERROR_REPORTING,
        help="""
        'error_reporting' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_ERROR_REPORTING)
    )
    parser.add_argument('--php-display-errors',
        default=DEFAULT_PHP_DISPLAY_ERRORS,
        help="""
        'display_errors' setting in php.ini. Defaults to '{}'
        """.format(DEFAULT_PHP_DISPLAY_ERRORS)
    )
    parser.add_argument('--composer-packages',
        help="""
        A comma separated list of PHP packages to install with Composer.
        """
    )
    parser.add_argument('--composer-working-directory',
        help="""
        If you provide '--composer-packages', this will be
        the directory in which packages are installed.
        """
    )
    parser.add_argument('--composer-project',
        help="""
        Pass this flag to create the specified Composer project.
        """
    )

    # All CMS
    # -------
    parser.add_argument('--admin-password',
        help="""
        Use this flag to provide the admin password of your CMS directly.
        This is not advised, and will only work if you also pass
        '--insecure-cli-password'. You should leave this blank instead,
        and Lampsible will prompt you for a password.
        """
    )

    # WordPress
    # ---------
    parser.add_argument('--wordpress-insecure-allow-xmlrpc',
        action='store_true',
        help="""
        Pass this flag if you want your WordPress site's insecure(!)
        endpoint xmlrpc.php to be reachable.
        This will make your site vulnerable to various exploits,
        and you really shouldn't do this if you don't have a good
        reason for this.
        """
    )
    # TODO
    # parser.add_argument('--wordpress-skip-content', action='store_true')

    # Web applications
    # ----------------
    parser.add_argument('--app-local-env', action='store_true',
        help="""
        Pass this flag if you want your web app to run with a "local" or "dev"
        type of configuration. Currently this affects the actions 'laravel'
        and 'suitecrm'. Only use this in internal test environments with no
        sensitive data, never on production environments!
        """
    )
    parser.add_argument('--laravel-artisan-commands',
        default=','.join(DEFAULT_LARAVEL_ARTISAN_COMMANDS),
        help="""
        a comma separated list of Artisan commands to run on your server after
        setting up your Laravel app there.
        Defaults to {}, which results in these commands being run: {}
        """.format(
            ','.join(DEFAULT_LARAVEL_ARTISAN_COMMANDS),
            '; '.join([
                'php /path/to/your/app/artisan {} --force'.format(artisan_command)
                for artisan_command in DEFAULT_LARAVEL_ARTISAN_COMMANDS
            ])
        )
    )

    # Misc
    # ----
    parser.add_argument('--insecure-cli-password', action='store_true',
        help="""
        If you want to pass passwords directly over the CLI,
        you have to pass this flag as well, otherwise Lampsible will
        refuse to run. This is not advised.
        """
    )
    parser.add_argument('--extra-packages',
        help="""
        comma separated list of any extra packages to be installed
        on the remote server
        """
    )
    parser.add_argument('--extra-env-vars', '-e',
        help="""
        comma separated list of any extra environment variables that you want
        to pass to your web app. If you are installing a Laravel app,
        these variables will be appended to your app's .env file.
        Otherwise, they'll be appended to Apache's envvars file,
        typically found in /etc/apache2/envvars.
        Example: SOME_VARIABLE=some-value,OTHER_VARIABLE=other-value
        """
    )

    # Metadata
    # --------
    parser.add_argument('-V', '--version',
        action='version',
        version=__version__
    )

    args = parser.parse_args()

    print(LAMPSIBLE_BANNER)

    validator = ArgValidator(args)
    result = validator.validate_args()

    if result != 0:
        print(dedent(
            """
            FATAL! Got invalid user input, and cannot continue.
            Please fix the issues listed above and try again.
            """
            ))
        return 1

    args = validator.get_validated_args()

    lampsible = Lampsible(
        web_user=args.web_user,
        web_host=args.web_host,
        action=args.action,
        private_data_dir=args.private_data_dir,
        apache_server_admin=args.apache_server_admin,
        apache_document_root=args.apache_document_root,
        apache_vhost_name=args.apache_vhost_name,
        # TODO: Improve this. The Lampsible library should handle this,
        # otherwise users will experience annoying errors.
        ssl_certbot=(not (
            args.insecure_no_ssl
            or args.ssl_selfsigned
            or args.action in [
                'dump-ansible-facts',
                'php',
                'mysql',
            ]
            )),
        ssl_selfsigned=args.ssl_selfsigned,
        ssl_test_cert=args.ssl_test_cert,
        email_for_ssl=args.email_for_ssl,
        database_root_password=args.database_root_password,
        database_username=args.database_username,
        database_password=args.database_password,
        database_name=args.database_name,
        database_host=args.database_host,
        database_table_prefix=args.database_table_prefix,
        database_system_user=args.database_system_user,
        database_system_host=args.database_system_host,
        php_version=args.php_version,
        php_extensions=args.php_extensions,
        php_memory_limit=args.php_memory_limit,
        php_upload_max_filesize=args.php_upload_max_filesize,
        php_post_max_size=args.php_post_max_size,
        php_max_execution_time=args.php_max_execution_time,
        php_max_input_time=args.php_max_input_time,
        php_max_file_uploads=args.php_max_file_uploads,
        php_allow_url_fopen=args.php_allow_url_fopen,
        php_error_reporting=args.php_error_reporting,
        php_display_errors=args.php_display_errors,
        composer_packages=args.composer_packages,
        composer_working_directory=args.composer_working_directory,
        composer_project=args.composer_project,
        site_title=args.site_title,
        admin_username=args.admin_username,
        admin_password=args.admin_password,
        admin_email=args.admin_email,
        wordpress_version=args.wordpress_version,
        wordpress_locale=args.wordpress_locale,
        wordpress_insecure_allow_xmlrpc=args.wordpress_insecure_allow_xmlrpc,
        joomla_version=args.joomla_version,
        joomla_admin_full_name=args.joomla_admin_full_name,
        drupal_profile=args.drupal_profile,
        app_name=args.app_name,
        app_build_path=args.app_build_path,
        laravel_artisan_commands=args.laravel_artisan_commands,
        app_local_env=args.app_local_env,
        suitecrm_version=args.suitecrm_version,
        suitecrm_demo_data=args.suitecrm_demo_data,
        extra_env_vars=args.extra_env_vars,
        extra_packages=args.extra_packages,
        ssh_key_file=args.ssh_key_file,
        remote_sudo_password=args.remote_sudo_password,
        ansible_galaxy_ok=args.ansible_galaxy_ok,
        interactive=True,
    )

    if args.action == 'dump-ansible-facts':
        # TODO: Refactor this.
        run_command(
            executable_cmd='ansible',
            cmdline_args=[
                '-i',
                '{}@{},'.format(
                    args.web_user,
                    args.web_host,
                ),
                'ungrouped',
                '-m',
                'setup'
            ]
        )
        lampsible.private_data_helper.cleanup_dir()
        return 0

    else:
        lampsible.run()

    return 0


if __name__ == '__main__':
    main()
