import os
from sys import path as sys_path
import argparse
import warnings
import yaml
from ansible_runner import Runner, RunnerConfig, run_command
from lampsible.constants import *
from lampsible.arg_validator import ArgValidator


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


def prepare_inventory(user, host):
    ########
    # TODO #
    ########

    # Dealing with inventories can be tricky.
    # This is a big part of what will have to be refactored in the future.
    # Ideally, it should be possible to pass the inventories to Ansible,
    # along with all sorts of variables, as a dictionary. However,
    # that appears not to be possible at the moment. If it truly is not
    # possible, this might be a worthwhile improvment to Ansible itself.
    # See the code below.

    # hosts = {hosts_ls[i]: users_ls[i] for i in range(l)}
    # inventory = {
    #     'ungrouped': {
    #         'hosts': {
    #             host: {'ansible_user': user} for host, user in hosts.items()
    #         },
    #         # various variables here...
    #     },
    # }

    # Without dictionaries, it would mean that we would have to create
    # some temporary files on the local filesystem to handle all the
    # inventory configuration. This is OK, but IMO not ideal. In any case,
    # I don't want to implement that into this project, but rather, into some
    # "Python-Ansible-Runner" library.

    # So for the time being, there are no "inventories-per-dictionary" (might
    # require changes to Ansible itself), nor "inventory-per-tmp-file" (won't
    # implement in this codebase, but rather in other library).

    # It's possible to pass "work around" the need for the "local inventory
    # file" by passing a comma separated list to Ansible. The commented out
    # code below does exactly that. However, dealing with multiple users and
    # hosts this way introduces unnecessary and unwieldy complexities, which
    # most of the time wouldn't be needed by a tool as simple as Lampsible
    # anyway. Funny thing... doing hosts and users this way works for the
    # ansible_runner module when we use it in this script, but does not work
    # for the ansible-runner as a CLI tool... even though in the venv 
    # they should be the same versions.

    # hosts_ls = hosts.split(',')
    # users_ls = users.split(',')
    # l = len(hosts_ls)
    # if len(users_ls) != l:
    #     raise NotImplementedError('For now, you have to pass users and hosts as lists that match one to one exactly. This will be improved in a future version.')

    # if l > 1: 
    #     hosts = ['{}@{}'.format(users_ls[i], hosts_ls[i]) for i in range(l)]
    #     return ','.join(hosts)
    # elif l == 1:
    #     return '{}@{},'.format(users_ls[0], hosts_ls[0])
    # else:
    #     raise ValueError('Got bad value for --users or --hosts.')

    # For these reasons, we confine ourselves for now to the simple
    # "one user, one host" inventory. Note the comma at the end of the
    # inventory string - that is needed, in order for Ansible to process it
    # this way.

    # To do the inventories "The Right Way", I want to find out, if it maybe
    # isn't possible to configure the entire invetory in one single
    # dictionary, and pass that directly to Ansible-Runner - and possibly
    # contribute those changes to the maintainers of Ansible itself. Failing
    # that, I want to implement some small library to handle tasks like
    # 'writing Anisble inventory file temporarily to local filesystem', which
    # would then be required by this application. 

    # Another thing that will be important in the future is for the web-
    # and database-servers to run on different hosts.
    return '{}@{},'.format(user, host)


def cleanup_private_data_dir(path):
    # TODO: Do this the right way.
    # TODO: Implement some safety measures to avoid data destruction.
    os.system('rm -r ' + path)


# TODO: See GH Issue #4. Currently the user is always prompted  for this.
# The user should only be prompted for this, when the requirements are not met.
def ensure_ansible_galaxy_dependencies(galaxy_requirements_file):
    ok_to_install = input("I have to download and install the Ansible Galaxy dependencies 'community.general', 'community.mysql' and 'community.crypto' into {}. Is this OK (yes/no)? ".format(
        os.path.join(USER_HOME_DIR, '.ansible/')
    )).lower()
    while ok_to_install != 'yes' and ok_to_install != 'no':
        ok_to_install = input("Please type 'yes' or 'no': ")
    if ok_to_install == 'yes':
        run_command(
            executable_cmd='ansible-galaxy',
            cmdline_args=['collection', 'install', '-r', galaxy_requirements_file],
        )
        # run_command(
        #     executable_cmd='ansible-galaxy',
        #     cmdline_args=['role', 'install', '-r', galaxy_requirements_file],
        # )
        return 0
    else:
        print('Cannot run Ansible plays without Galaxy requirements. Aborting.')
        return 1



def main():
    parser = argparse.ArgumentParser(
        prog='lampsible',
        description='Deploy and set up LAMP Stacks with Ansible',
        epilog='Currently in development...',
    )
    # TODO
    parser.add_argument('user')
    parser.add_argument('host')

    # TODO: Validation
    parser.add_argument('action', choices=[
        # LAMP-Stack basics
        'lamp-stack',
        'apache',
        'mysql',
        'php',
        # PHP CMS
        'wordpress',
        'typo3',       # TODO
        'joomla',      # TODO
        'drupal',      # TODO
        # PHP frameworks
        'laravel',     # TODO
        'symfony',     # TODO
        'zend',        # TODO
        # Local debugging
        'dump-ansible-facts',
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

    # APACHE
    ########
    # TODO: Apache configs, versions, etc? Nginx or others?
    parser.add_argument('--apache-vhost-name',
        default=DEFAULT_APACHE_VHOST_NAME)
    parser.add_argument('--apache-server-admin',
        default=DEFAULT_APACHE_SERVER_ADMIN)
    parser.add_argument('--apache-document-root',
        default=DEFAULT_APACHE_DOCUMENT_ROOT)

    # DATABASE
    #######
    # TODO: MySQL configs, versions, etc? PostgreSQL or others?
    parser.add_argument('--database-engine', default=DEFAULT_DATABASE_ENGINE)
    parser.add_argument('--database-username')
    parser.add_argument('--database-password')
    parser.add_argument('--database-name')
    # TODO; Right now, this is not possible. To enable this, you have to dive
    # a little deeper into Ansible's inventory feature... for now, the
    # database and webserver need to run on the same host.
    parser.add_argument('--database-host', default=DEFAULT_DATABASE_HOST)
    parser.add_argument('--database-table-prefix',
        default=DEFAULT_DATABASE_TABLE_PREFIX)

    # PHP
    #####
    parser.add_argument('--php-version', default='8.2')
    parser.add_argument('--skip-php-extensions', action='store_true')
    # TODO
    parser.add_argument('--php-my-admin', action='store_true')


    # WORDPRESS
    ###########
    # TODO: Figure this out, and a better way to validate this.
    # parser.add_argument('--wordpress-version', choices=['?'], default='latest?')
    parser.add_argument('--wordpress-version', default='6.4')
    parser.add_argument('--wordpress-auth-key')
    parser.add_argument('--wordpress-secure-auth-key')
    parser.add_argument('--wordpress-logged-in-key')
    parser.add_argument('--wordpress-nonce-key')
    parser.add_argument('--wordpress-auth-salt')
    parser.add_argument('--wordpress-secure-auth-salt')
    parser.add_argument('--wordpress-logged-in-salt')
    parser.add_argument('--wordpress-nonce-salt')
    parser.add_argument('--wordpress-insecure-allow-xmlrpc', action='store_true')

    # ANSIBLE RUNNER
    ################
    parser.add_argument('--ssh-key-file')
    parser.add_argument('--private-data-dir', default=DEFAULT_PRIVATE_DATA_DIR)
    parser.add_argument('--project-dir',      default=DEFAULT_PROJECT_DIR)
    parser.add_argument('--keep-private-data-dir', action='store_true')

    # SSL
    #####
    parser.add_argument('--ssl-certbot', action='store_true')
    parser.add_argument('--ssl-selfsigned', action='store_true')
    parser.add_argument('--email-for-ssl')
    parser.add_argument('--domains-for-ssl')
    parser.add_argument('--test-cert', action='store_true')

    # TODO: This is intended as a temporary workaround.
    # Ideally, we implement https://github.com/saint-hilaire/lampsible/issues/14
    # and then there should be no need to configure the length of time for
    # which Ansible pauses to allow the user to perform this step (unless
    # the user wants to do it in the browser, via some
    # --wordpress-interactive-install?)
    # Failing that, it would be quite good if a future version of
    # Ansible Runner can improve the handling of user input in the context
    # of paused Playbooks (see issues
    # https://github.com/ansible/ansible-runner/issues/1075
    # and https://github.com/ansible/ansible-runner/issues/756):
    parser.add_argument('--wordpress-5-minute-install-seconds', default=120)

    # MISC
    ######
    parser.add_argument('--insecure-cli-password', action='store_true')
    parser.add_argument('--insecure-skip-fail2ban', action='store_true')

    args = parser.parse_args()

    validator = ArgValidator(args)
    result = validator.validate_args()
    if result != 0:
        print('FATAL! validator.validate_args returned non zero return code. Aborting.')
        return 1
    args = validator.get_args()

    # TODO: Let arg_validator handle private_data_dir, project_dir,
    # inventory and playbook as well, but for now, this will do.
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

    inventory = prepare_inventory(args.user, args.host)
    # Now inventory is something like 'user1@host1,user2@host2' 
    # or 'user1@host1,'

    galaxy_result = ensure_ansible_galaxy_dependencies(os.path.join(
        project_dir, 'ansible-galaxy-requirements.yml'))

    # TODO: SyntaxWarning: "is" with a literal. Did you mean "=="?
    if galaxy_result is 1:
        return 0


    if args.action == 'dump-ansible-facts':
        # TODO: Perhaps we can improve this. For example, if we refactor
        # the handling of inventories, we could do this with Ansible Runner's
        # 'module' feature (that is, pass the kwargs module='setup' to the
        # configuration).
        # However, for now, this also works quite well.
        run_command(
            executable_cmd='ansible',
            cmdline_args=['-i', inventory, 'ungrouped', '-m', 'setup'],
        )
        return 0

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

    apache_vhosts = validator.get_apache_vhosts()
    apache_custom_conf_name = validator.get_apache_custom_conf_name()

    wordpress_auth_vars = validator.get_wordpress_auth_vars()

    rc = RunnerConfig(
        private_data_dir=private_data_dir,
        project_dir=project_dir,

        inventory=inventory,

        extravars={
            'apache_vhosts': apache_vhosts,
            'apache_custom_conf_name': apache_custom_conf_name,
            'database_username': args.database_username,
            'database_password': args.database_password,
            'database_host': args.database_host,
            'database_name': args.database_name,
            'database_table_prefix': args.database_table_prefix,
            'php_version': args.php_version,
            'skip_php_extensions': args.skip_php_extensions,
            'wordpress_version': args.wordpress_version,
            'wordpress_auth_vars': wordpress_auth_vars,
            'wordpress_insecure_allow_xmlrpc': args.wordpress_insecure_allow_xmlrpc,
            'ssl_certbot': args.ssl_certbot,
            'ssl_selfsigned': args.ssl_selfsigned,
            'email_for_ssl': args.email_for_ssl,
            'certbot_domains_string': validator.get_certbot_domains_string(),
            'certbot_test_cert_string': validator.get_certbot_test_cert_string(),
            # TODO: Improve this when we fix Certbot.
            'domain_for_wordpress': validator.get_domain_for_wordpress(),
            'wordpress_5_minute_install_seconds': args.wordpress_5_minute_install_seconds,
            'insecure_skip_fail2ban': args.insecure_skip_fail2ban,
        },
        playbook=playbook,
    )

    if args.ssh_key_file:
        try:
            with open(os.path.abspath(args.ssh_key_file), 'r') as key_file:
                key_data = key_file.read()
            rc.ssh_key_data = key_data
        except FileNotFoundError:
            print('Warning! SSH key file not found!')

    rc.prepare()
    r = Runner(config=rc)
    r.run()

    # TODO: Deal with these better.
    print(r.stats)

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
