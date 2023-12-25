import os
from sys import path as sys_path
import argparse
import warnings
import yaml
from ansible_runner import Runner, RunnerConfig

USER_HOME_DIR = os.path.expanduser('~')

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

def init_private_data_dir():
    # For now, just doing this in user's ~/.lampsible
    private_data_dir = os.path.join(USER_HOME_DIR, '.lampsible')
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
    raise NotImplementedError()
    main_rc = RunnerConfig(
        private_data_dir=private_data_dir,
        project_dir=project_dir,

        inventory=inventory,

        extravars={
            'php_version':           kwargs['php_version'],
            'database_username':     kwargs['database_username'],
            'database_password':     kwargs['database_password'],
            'database_name':         kwargs['database_name'],
            'database_table_prefix': kwargs['database_table_prefix'],
            'wordpress_version':     kwargs['wordpress_version'],
        },
        playbook=playbook
    )
    try:
        ssl_action = kwargs['ssl_action']
        assert ssl_action in ['certbot', 'selfsigned']
    except (KeyError, AssertionError) as e:
        return [main_rc]

    return_list = [
        main_rc,
        RunnerConfig(
            private_data_dir=private_data_dir,
            project_dir=project_dir,

            inventory=inventory,

            extravars={
                'email_for_ssl':   kwargs['email_for_ssl'],
                'domains_for_ssl': kwargs['domains_for_ssl'],
            },
            playbook='ssl-{}.yml'.format(ssl_action)
        )
    ]
    if playbook == 'wordpress.yml' and ssl_action == 'certbot':
        # TODO: This part is especially ugly... as if it's not bad enough,
        # that we have to run 2 separate plays, because we can't get SSL
        # right on the first play, here we run a third play, and run raw SQL
        # queries as root to tweak some more configurations.
        domain_for_wordpress = kwargs['domains_for_ssl'].split(',')[0]
        return_list.append(
            RunnerConfig(
                private_data_dir=private_data_dir,
                project_dir=project_dir,

                inventory=inventory,

                extravars={
                    'domain_for_wordpress': domain_for_wordpress,
                    'database_name':         kwargs['database_name'],
                    'database_table_prefix': kwargs['database_table_prefix'],
                },
                playbook='domain-for-wordpress.yml'
            )
        )

    return return_list

def get_ssl_action(certbot, selfsigned):
    if certbot:
        if selfsigned:
            warnings.warn('Warning: Got --ssl-certbot, but also got --ssl-selfsigned. Ignoring --ssl-selfsigned and using --ssl-certbot.')
        return 'certbot'
    elif selfsigned:
        warnings.warn('Warning! Creating a self signed certificate to handle the site\'s encryption. This is less secure and will appear untrustworthy to any visitors. Only use tthis for testing environments.')
        return 'selfsigned'
    else:
        warnings.warn('WARNING! Your site will not have any encryption enabled! This is very insecure, as passwords and other sensitive data will be transmitted in clear text. DO NOT use this on any remote host or over any partially untrusted network. ONLY use this for local, secure, private and trusted networks, ideally only for local development servers.')
        return None


def main():
    parser = argparse.ArgumentParser(
        prog='Lampsible',
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
    # TODO: Support other distros, validation for versions, etc.
    parser.add_argument('--distro', choices=['Ubuntu'], default='Ubuntu')
    parser.add_argument('--distro-version', default=22)

    # TODO: Apache configs, versions, etc? Nginx or others?
    # TODO: MySQL configs, versions, etc? PostgreSQL or others?
    parser.add_argument('--database-engine', default='mysql')

    # TODO: Constants for default values
    parser.add_argument('--database-username', default='db-username')
    parser.add_argument('--database-password', default='db-password')
    parser.add_argument('--database-name', default='db_name')
    # TODO; Right now, this is not possible. To enable this, you have to dive
    # a little deeper into Ansible's inventory feature... for now, the
    # database and webserver need to run on the same host.
    parser.add_argument('--database-host', default='localhost')

    parser.add_argument('--database-table-prefix', default='')

    # TODO: PHP is not working out of the box. At least for WordPress, likely for Laravel
    # and other frameworks, it will complain about missing extensions, at least -mysql,
    # probably others. The reason it worked before in other tests was that we happened
    # to also install phpmyadmin via Ansible. phpmyadmin apparently installs the
    # necessary PHP extensions onto the system.
    parser.add_argument('--php-version', default='8.2')

    # TODO: Figure this out, and a better way to validate this.
    # parser.add_argument('--wordpress-version', choices=['?'], default='latest?')
    parser.add_argument('--wordpress-version', default='6.0')

    # TODO
    # parser.add_argument('--private-data-dir', default=DEFAULT_PRIVATE_DATA_DIR)
    # parser.add_argument('--project-dir', default=DEFAULT_PROJECT_DIR)

    # TODO
    parser.add_argument('--php-my-admin', action='store_true')

    # TODO
    parser.add_argument('--ssl-certbot', action='store_true')
    parser.add_argument('--ssl-selfsigned', action='store_true')
    parser.add_argument('--email-for-ssl')
    parser.add_argument('--domains-for-ssl')

    args = parser.parse_args()

    # TODO: Much of this code doesn't work :-(
    # In particular, the SSL stuff causes trouble.
    # It runs without throwing errors, but it breaks the server.
    if args.distro != 'Ubuntu' \
        or args.database_engine != 'mysql' \
        or args.database_host != 'localhost' \
        or args.php_my_admin \
        or args.ssl_certbot \
        or args.ssl_selfsigned:

        raise NotImplementedError()

    # Handle defaults.
    # TODO: Improve this. Defaults should be read from some constant.
    # We should warn the  user about this, or even ask confirmation.
    if args.action == 'wordpress':
        if args.database_name == 'db_name':
            args.database_name = 'wordpress'
        if args.database_table_prefix == '':
            args.database_table_prefix = 'wp_'

    ssl_action = get_ssl_action(args.ssl_certbot, args.ssl_selfsigned)

    # TODO: Validate these variables better, and raise more appropriate exceptions.
    if ssl_action is not None and args.email_for_ssl is None:
        raise ValueError('When passing --ssl-*, you must also pass --email-for-ssl.')
    if ssl_action == 'certbot' and args.domains_for_ssl is None:
        warnings.warn('Warning! Got --ssl-certbot but no --domains-for-ssl. Defaulting to value of `hosts`.')
        # TODO: Fix this strange behavior that we have forced ourselves into.
        args.domains_for_ssl = list(set(args.hosts))
        if args.action == 'wordpress':
            # TODO: This especially please make it better.
            args.domains_for_ssl.append('www.{}'.format(args.domains_for_ssl[0]))
    if isinstance(args.domains_for_ssl, list):
        domains_for_ssl = ','.join(args.domains_for_ssl)
    else:
        domains_for_ssl = args.hosts[0]

    if args.php_my_admin:
        warnings.warn("WARNING: Got --php-my-admin, which is not implemented yet. This flag will be ignored.")
    
    private_data_dir = init_private_data_dir()
    project_dir=os.path.join(sys_path[0], 'project')

    # import pdb; pdb.set_trace()
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
    # runner_configs = make_runner_configs(
    #     private_data_dir=private_data_dir,
    #     project_dir=project_dir,
    #     inventory=inventory,
    #     playbook=playbook,
    #     php_version=args.php_version,
    #     database_username=args.database_username,
    #     database_password=args.database_password,
    #     database_name=args.database_name,
    #     database_table_prefix=args.database_table_prefix,
    #     wordpress_version=args.wordpress_version,
    #     ssl_action=ssl_action,
    #     email_for_ssl=args.email_for_ssl,
    #     domains_for_ssl=domains_for_ssl,
    # )
    # for rc in runner_configs:
    #     rc.prepare()
    #     r = Runner(config=rc)
    #     r.run()
    #     print(r.stats)
    ########################################

    ########################################
    rc = RunnerConfig(
        private_data_dir=private_data_dir,
        project_dir=project_dir,

        inventory=inventory,

        extravars={
            'php_version': args.php_version,
            'database_username': args.database_username,
            'database_password': args.database_password,
            'database_name': args.database_name,
            'database_table_prefix': args.database_table_prefix,
            'wordpress_version': args.wordpress_version,
            # TODO
            # 'ssl_action'=ssl_action,
            # 'email_for_ssl'=args.email_for_ssl,
            # 'domains_for_ssl'=domains_for_ssl,
        },
        playbook=playbook,
    )
    rc.prepare()
    # rc.prepare_env()
    # rc.prepare_inventory()
    # rc.prepare_command()
    r = Runner(config=rc)
    r.run()

    # TODO: Deal with these better.
    print(r.stats)
    ########################################

    cleanup_private_data_dir(private_data_dir)
    return 0


    # TODO: Some other ideas...
    # -------------------------
    # It would be cool if we could also use this to run Ansible
    # directly. See ansible_runner.run_command.

if __name__ == '__main__':
    main()
