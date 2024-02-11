import os
from sys import path as sys_path
import argparse
import warnings
import yaml
from ansible_runner import Runner, RunnerConfig, run_command

############
# DEFAULTS #
############

# SCRIPT PATHS
USER_HOME_DIR            = os.path.expanduser('~')
DEFAULT_PRIVATE_DATA_DIR = os.path.join(USER_HOME_DIR, '.lampsible')
# If the user does not supply a value, this will be overwritten by a path
# inside the package installation, which we detect later on.
DEFAULT_PROJECT_DIR      = ''

# DATABASE
DEFAULT_DATABASE_ENGINE       = 'mysql'
DEFAULT_DATABASE_USERNAME     = 'db-username'
DEFAULT_DATABASE_PASSWORD     = 'db-password'
DEFAULT_DATABASE_NAME         = 'db_name'
DEFAULT_DATABASE_HOST         = 'localhost'
DEFAULT_DATABASE_TABLE_PREFIX = ''

# TODO
def parse_action(action):
    return
    # action_mapping = {
    #     # lamp-stack works, the others should too.
    #     'lamp-stack': 'lamp-stack.yml',
    #     'phpmyadmin': 'lamp-stack.yml',
    #     'wordpress': 'wordpress.yml',
    #     # TODO: These don't work.
    #     # # This implies 'roles'
    #     # 'apache': [
    #     #     'apt-update',
    #     #     'apache2',
    #     # ],
    #     # 'mysql': [
    #     #     'apt-update',
    #     #     'mysql',
    #     # ],
    #     # 'php': [
    #     #     'apt-update',
    #     #     'apache2',
    #     #     'mysql',
    #     # ],
    # }

    # if action not in action_mapping:
    #     raise ValueError('Got bad action')

    # result = action_mapping[action]
    # if '.yml' in result:
    #     return {'playbook': result}
    # # TODO Not working
    # # elif isinstance(result, list):
    # #     return {'roles': result}
    # else:
    #     raise ValueError('Got bad action')

# TODO
def init_directories(hosts, private_data_dir, project_dir,):
    pass
    # directories = {
    #     'private_data_dir': init_private_data_dir(
    #         os.path.abspath(private_data_dir),
    #         hosts
    #     ),
    #     'project_dir': init_project_dir(
    #         os.path.abspath(project_dir)
    #     ),
    # }
    # for k,v in directories.items():
    #     try:
    #         assert os.path.isdir(v)
    #     except AssertionError:
    #         raise ValueError('{} is not a valid {}'.format(k, v))
    # return directories

def init_private_data_dir(private_data_dir):
    try:
        os.makedirs(private_data_dir)
    except PermissionError:
        private_data_dir = os.path.join(USER_HOME_DIR, '.lampsible')
        print('Could not write specified directory. Defaulting to {}'.format(
            private_data_dir = os.path.join(USER_HOME_DIR, '.lampsible')
        ))
        os.makedirs(private_data_dir)
    except FileExistsError:
        pass

    return os.path.abspath(private_data_dir)

def init_project_dir(project_dir):
    if project_dir == '':
        # TODO: There are some problems with "editable" pip installs.
        return find_package_project_dir()
    return project_dir

def find_package_project_dir():
    for path_str in sys_path:
        try:
            try_path = os.path.join(path_str, 'lampsible', 'project')
            assert os.path.isdir(try_path)
            return try_path
        except AssertionError:
            pass
    raise RuntimeError("Got no user supplied --project-dir, and could not find one in expected package location. Your Lampsible installation is likely broken. However, if you are running this code directly from source, this is expected behavior. You probably forgot to pass the '--project-dir' flag. The directoy you're looking for is 'src/lampsible/project/'.")

def init_inventory_file(private_data_dir, user, host):
    pass
    # try:
    #     os.mkdir(os.path.join(private_data_dir, 'inventory'))
    # except FileExistsError:
    #     pass
    #     
    # inventory = {
    #     'ungrouped': {
    #         'hosts': {
    #             host: {'ansible_user': user}
    #         },
    #     },
    # }
    # with open(os.path.join(private_data_dir, 'inventory', 'hosts'), 'w') as fh:
    #     fh.write(yaml.dump(inventory))

def prepare_inventory(users, hosts):
    # TODO: Funny thing... doing hosts and users this way works for the
    # ansible_runner module when we use it in this script, but does not work
    # for the ansible-runner as a CLI tool... even though in the venv 
    # they should be the same versions.
    hosts_ls = hosts.split(',')
    users_ls = users.split(',')
    l = len(hosts_ls)
    if len(users_ls) != l:
        raise NotImplementedError('For now, you have to pass users and hosts as lists that match one to one exactly. This will be improved in a future version.')

    if l > 1: 
        hosts = ['{}@{}'.format(users_ls[i], hosts_ls[i]) for i in range(l)]
        return ','.join(hosts)
    elif l == 1:
        return '{}@{},'.format(users_ls[0], hosts_ls[0])
    else:
        raise ValueError('Got bad value for --users or --hosts.')
    
    # TODO: Passing an inventory directly as a dictionary to Ansible is currenlty
    # not possible... unfortunately! It should be...
    # hosts = {hosts_ls[i]: users_ls[i] for i in range(l)}

    # inventory = {
    #     'ungrouped': {
    #         'hosts': {
    #             host: {'ansible_user': user} for host, user in hosts.items()
    #         },
    #     },
    # }

    # return inventory

def cleanup_private_data_dir(path):
    # TODO: Do this the right way.
    # TODO: Implement some safety measures to avoid data destruction.
    os.system('rm -r ' + path)

# TODO: This is a very ugly workaround to an equally ugly antipattern from
# the legacy implementation. It works, but overall, SSL does not.
# In the short term, SSL needs to work like this, but in the long term,
# this will be refactored anyway.
def make_runner_configs(*, private_data_dir, project_dir, inventory,
    playbook, **kwargs):
    main_rc = RunnerConfig(
        private_data_dir=private_data_dir,
        project_dir=project_dir,

        inventory=inventory,

        extravars={
            'php_version':           kwargs['php_version'],
            'skip_php_extensions':   kwargs['skip_php_extensions'],
            'database_username':     kwargs['database_username'],
            'database_password':     kwargs['database_password'],
            'database_name':         kwargs['database_name'],
            'database_table_prefix': kwargs['database_table_prefix'],
            'wordpress_version':     kwargs['wordpress_version'],
            'apache_document_root':  kwargs['apache_document_root'],
        },
        playbook=playbook
    )
    try:
        ssl_action = kwargs['ssl_action']
        assert ssl_action in ['certbot', 'selfsigned']
    except (KeyError, AssertionError) as e:
        return [main_rc]

    # TODO: Implement some function to turn the domains,
    # (if it's a WordPress site) to something like
    # ' -d thedomain.com -d www.thedomain.com '.
    # Also, see how it's implemented in dawn
    # Also, see https://eff-certbot.readthedocs.io/en/latest/using.html#certbot-commands
    # for how to do it 'right'.
    # But overall, this try-except block needs to be replaced.
    try:
        domains_for_ssl = ','.join(kwargs['domains_for_ssl'])
    except TypeError:
        domains_for_ssl = ''

    return_list = [
        main_rc,
        RunnerConfig(
            private_data_dir=private_data_dir,
            project_dir=project_dir,

            inventory=inventory,

            extravars={
                'email_for_ssl':        kwargs['email_for_ssl'],
                'domains_for_ssl':      domains_for_ssl,
                'apache_document_root': kwargs['apache_document_root'],
            },
            playbook='ssl-{}.yml'.format(ssl_action)
        )
    ]

    if playbook == 'wordpress.yml' and ssl_action == 'certbot':
        # TODO: This part should especially be refactored...
        # By now, we will have run 2 plays to install
        # everything and to set up SSL. Here we run a
        # third play to configure a WordPress setting for the domain in the
        # database. In the future, we will improve the SSL handling, and can
        # hopefully do it all more elegantly.
        domain_for_wordpress = kwargs['domains_for_ssl'][0]
        return_list.append(
            RunnerConfig(
                private_data_dir=private_data_dir,
                project_dir=project_dir,

                inventory=inventory,

                extravars={
                    'domain_for_wordpress':  domain_for_wordpress,
                    'database_name':         kwargs['database_name'],
                    'database_table_prefix': kwargs['database_table_prefix'],
                    'apache_document_root':  kwargs['apache_document_root'],
                },
                playbook='domain-for-wordpress.yml'
            )
        )

    return return_list

def get_ssl_action(certbot, selfsigned):
    if certbot:
        warnings.warn('Warning! Got --ssl-certbot. This is by far the most sensible SSL configuration, but unfortunately, it is not properly working yet in this tool :-(\n\nPlease consider reaching out to me and helping me implement this feature ;-)\nhttps://github.com/saint-hilaire')
        warnings.warn('IMPORTANT!! You have to SSH to your webserver and run Certbot there. Also, be aware that WordPress sites require www.your-example-domain.com along with your-example-domain.com to be set up - you have to pass both domains to Certbot, if you are installing a WordPress site. Until this is taken care of, YOUR SITE WILL NOT HAVE WORKING SSL-ENCRYPTION! Thank you for your understanding.')
        from time import sleep
        sleep(4)
        if selfsigned:
            warnings.warn('Warning: Got --ssl-certbot, but also got --ssl-selfsigned. Ignoring --ssl-selfsigned and using --ssl-certbot.')
        return 'certbot'
    elif selfsigned:
        warnings.warn('Warning! Creating a self signed certificate to handle the site\'s encryption. This is less secure and will appear untrustworthy to any visitors. Only use this for testing environments.')
        return 'selfsigned'
    else:
        warnings.warn('WARNING! Your site will not have any encryption enabled! This is very insecure, as passwords and other sensitive data will be transmitted in clear text. DO NOT use this on any remote host or over any partially untrusted network. ONLY use this for local, secure, private and trusted networks, ideally only for local development servers.')
        return None

# TODO
def get_document_root_from_action(action):
    if action == 'wordpress':
        return '/var/www/html/wordpress'
    else:
        return '/var/www/html'

def main():
    parser = argparse.ArgumentParser(
        prog='lampsible',
        description='Deploy and set up LAMP Stacks with Ansible',
        epilog='Currently in development...',
    )
    # TODO
    parser.add_argument('users')
    parser.add_argument('hosts')

    # TODO: Validation
    parser.add_argument('action', choices=[
        # LAMP-Stack basics
        'lamp-stack',
        'apache',
        'php',
        'mysql',
        # PHP CMS
        'wordpress',
        'typo3',       # TODO
        'joomla',      # TODO
        'drupal',      # TODO
        'shopweezle',  # TODO
        # PHP frameworks
        'laravel',     # TODO
        'symfony',     # TODO
        'zend',        # TODO
        # Non-PHP frameworks. Should we even support these?
        'django',      # TODO
        'rails',       # TODO
        'springboot',  # TODO
        # Misc. PHP
        'magento',     # TODO
        'woocommerce', # TODO
        'composer',    # TODO
        'xdebug',      # TODO
        ]
    )
    # TODO: Because the OS will have been installed before this script executes,
    # and because this script does not intend to influence the OS further, this
    # option is superfluous.
    # However, we do need to know the OS version for validation. So we should
    # be able to detect it from the host somehow.
    # parser.add_argument('--distro', choices=['Ubuntu'], default='Ubuntu')
    # parser.add_argument('--distro-version', default=22)

    # TODO: Apache configs, versions, etc? Nginx or others?
    # TODO: MySQL configs, versions, etc? PostgreSQL or others?
    parser.add_argument('--database-engine', default=DEFAULT_DATABASE_ENGINE)

    parser.add_argument('--database-username',
        default=DEFAULT_DATABASE_USERNAME)
    # TODO: feature/fix-secrets
    parser.add_argument('--database-password',
        default=DEFAULT_DATABASE_PASSWORD)
    parser.add_argument('--database-name', default=DEFAULT_DATABASE_NAME)
    # TODO; Right now, this is not possible. To enable this, you have to dive
    # a little deeper into Ansible's inventory feature... for now, the
    # database and webserver need to run on the same host.
    parser.add_argument('--database-host', default=DEFAULT_DATABASE_HOST)

    parser.add_argument('--database-table-prefix',
        default=DEFAULT_DATABASE_TABLE_PREFIX)

    # NOTE:
    # * Ubuntu versions 20 and older do not support PHP versions 8.0 or newer
    # * Ubuntu 22 does not support PHP 8.0. PHP 8.1 is supported.
    # To work around the above points, you would have to manually configure the
    # APT repository.
    parser.add_argument('--php-version', default='8.2')

    # TODO: Figure this out, and a better way to validate this.
    # parser.add_argument('--wordpress-version', choices=['?'], default='latest?')
    parser.add_argument('--wordpress-version', default='6.0')
    parser.add_argument('--skip-php-extensions', action='store_true')

    parser.add_argument('--private-data-dir', default=DEFAULT_PRIVATE_DATA_DIR)
    parser.add_argument('--project-dir',      default=DEFAULT_PROJECT_DIR)

    # TODO
    parser.add_argument('--php-my-admin', action='store_true')

    # TODO
    parser.add_argument('--ssl-certbot', action='store_true')
    parser.add_argument('--ssl-selfsigned', action='store_true')
    parser.add_argument('--email-for-ssl')
    parser.add_argument('--domains-for-ssl')

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--keep-private-data-dir', action='store_true')

    args = parser.parse_args()

    if args.database_engine != DEFAULT_DATABASE_ENGINE \
        or args.database_host != DEFAULT_DATABASE_HOST \
        or args.php_my_admin:

        raise NotImplementedError()

    # Handle defaults.
    # TODO: Improve this. Defaults should be read from some constant.
    # We should warn the  user about this, or even ask confirmation.
    if args.action == 'wordpress':
        if args.database_name == DEFAULT_DATABASE_NAME:
            args.database_name = 'wordpress'
        if args.database_table_prefix == DEFAULT_DATABASE_TABLE_PREFIX:
            args.database_table_prefix = 'wp_'

    # TODO: Make it DRY
    if args.database_username == DEFAULT_DATABASE_USERNAME:
        warnings.warn('WARNING! Got no --database-username. Defaulting to '
            + DEFAULT_DATABASE_USERNAME + '. This is insecure!'
        )
    if args.database_password == DEFAULT_DATABASE_PASSWORD:
        warnings.warn('WARNING! Got no --database-password. Defaulting to '
            + DEFAULT_DATABASE_PASSWORD + '. This is insecure!'
        )

    ssl_action = get_ssl_action(args.ssl_certbot, args.ssl_selfsigned)

    # TODO: Validate these variables better, and raise more appropriate exceptions.
    if ssl_action is not None and args.email_for_ssl is None:
        raise ValueError('When passing --ssl-*, you must also pass --email-for-ssl.')
    if ssl_action == 'certbot' and args.domains_for_ssl is None:
        warnings.warn('Warning! Got --ssl-certbot but no --domains-for-ssl. Defaulting to value of `hosts`.')
        # TODO: Fix this strange behavior that we have forced ourselves into.
        args.domains_for_ssl = args.hosts.split(',')
        if args.action == 'wordpress':
            # TODO: This especially please make it better.
            args.domains_for_ssl.append('www.{}'.format(args.domains_for_ssl[0]))

    if args.php_my_admin:
        warnings.warn("WARNING: Got --php-my-admin, which is not implemented yet. This flag will be ignored.")
    
    if args.skip_php_extensions:
        warnings.warn('Will not install common PHP extensions. WordPress, Laravel, and other common CMS or frameworks will probably not work.')

    # TODO: We need to validate against OS type and version, but this
    # information should be detected by the script, not supplied by the user
    # via CLI args.
    # if args.distro == 'Ubuntu' and int(args.distro_version) <= 20 \
    #     and float(args.php_version) > 7.4:
    #     warnings.warn('Trying to install a PHP version newer than 7.4 on an Ubuntu version 20 or older. This will likely not work.')

    private_data_dir = init_private_data_dir(args.private_data_dir)

    # TODO: Where to put this?
    # Putting it directly into the package build seems the more simple and
    # intuitive approach.
    # However, placing it into another path on the system, for example
    # ~/.lampsible/ offers the benefit of making the path of project_dir
    # configurable by the user. In this case, ~/.lampsible could be the
    # default value, but if users override this, they could provide their own
    # playbooks.
    # For now, let's simply bring the directory directly into the package
    # build.
    project_dir = init_project_dir(args.project_dir)

    inventory = prepare_inventory(args.users, args.hosts)
    # Now inventory is something like 'user1@host1,user2@host2' 
    # or 'user1@host1,'

    # TODO
    # action = parse_action(args.action)
    # if 'playbook' in action:
    #     playbook = action['playbook']
    #     roles = None
    # elif 'roles' in action:
    #     # TODO
    #     # playbook = 'do-nothing.yml'
    #     # roles = action['roles']
    #     raise NotImplementedError()
    # else:
    #     raise NotImplementedError()
    playbook = '{}.yml'.format(args.action)
    if not os.path.exists(os.path.join(project_dir, playbook)):
        # TODO: In the future we will have to change how this is validated.
        raise NotImplementedError()

    apache_document_root = get_document_root_from_action(args.action)
    # TODO
    # if roles and len(roles) > 1:
    #     roles = ','.join(roles) 
    # elif roles:
    #     roles = roles.pop()

    # TODO: This is a very ugly workaround to an equally ugly antipattern from
    # the legacy implementation. It works, but overall, SSL does not.
    # In the short term, SSL needs to work like this, but in the long term,
    # this will be refactored anyway.
    ########################################
    runner_configs = make_runner_configs(
        private_data_dir=private_data_dir,
        project_dir=project_dir,
        inventory=inventory,
        playbook=playbook,
        php_version=args.php_version,
        skip_php_extensions=args.skip_php_extensions,
        database_username=args.database_username,
        database_password=args.database_password,
        database_name=args.database_name,
        database_table_prefix=args.database_table_prefix,
        wordpress_version=args.wordpress_version,
        ssl_action=ssl_action,
        email_for_ssl=args.email_for_ssl,
        domains_for_ssl=args.domains_for_ssl,
        apache_document_root=apache_document_root,
    )
    if args.debug:
        # TODO: Perhaps we can improve this. For example, if we refactor
        # the handling of inventories, we could do this with Ansible Runner's
        # 'module' feature (that is, pass the kwargs module='setup' to the
        # configuration).
        # However, for now, this also works quite well.
        run_command(
            executable_cmd='ansible',
            cmdline_args=['-i', inventory, 'ungrouped', '-m', 'setup'],
        )
    else:
        for rc in runner_configs:
            rc.prepare()
            r = Runner(config=rc)
            r.run()
            # TODO: Deal with these better.
            print(r.stats)
    ########################################

    ########################################
    # rc = RunnerConfig(
    #     private_data_dir=private_data_dir,
    #     project_dir=project_dir,

    #     inventory=inventory,

    #     extravars={
    #         'php_version': args.php_version,
    #         'skip_php_extensions': args.skip_php_extensions,
    #         'database_username': args.database_username,
    #         'database_password': args.database_password,
    #         'database_name': args.database_name,
    #         'database_table_prefix': args.database_table_prefix,
    #         'wordpress_version': args.wordpress_version,
    #         'apache_document_root': apache_document_root,
    #     },
    #     playbook=playbook,
    # )
    # rc.prepare()
    # # rc.prepare_env()
    # # rc.prepare_inventory()
    # # rc.prepare_command()
    # r = Runner(config=rc)
    # r.run()

    # # TODO: Deal with these better.
    # print(r.stats)
    ########################################

    if not args.keep_private_data_dir:
        cleanup_private_data_dir(private_data_dir)
    else:
        print('WARNING! Got --keep-private-data-dir, probably because you are debugging something locally, so I will not delete the directory {}. Please be aware that it likely contains sensitive data, like SSH keys and so on, so you should probably delete it yourself.'.format(private_data_dir))
        # TODO: warnings gets tripped up by strings like this :-(
        # warnings.warn('WARNING! Got --keep-private-data-dir, probably because you are debugging something locally, so I will not delete the directory {}. Please be aware that it likely contains sensitive data, like SSH keys and so on, so you should probably delete it yourself.'.format(private_data_dir))

    return 0

    # TODO: Some other ideas...
    # -------------------------
    # It would be cool if we could also use this to run Ansible
    # directly. See ansible_runner.run_command.

if __name__ == '__main__':
    main()
