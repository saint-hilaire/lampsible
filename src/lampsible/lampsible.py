import os
import warnings
from yaml import safe_load
from shutil import rmtree
from ansible_runner import Runner, RunnerConfig, run_command
from . import __version__
from lampsible.constants import *
from lampsible.arg_validator import ArgValidator


# def init_private_data_dir(private_data_dir):
#     try:
#         os.makedirs(private_data_dir)
#     except PermissionError:
#         private_data_dir = os.path.join(USER_HOME_DIR, '.lampsible')
#         print('Could not write specified directory. Defaulting to {}'.format(
#             private_data_dir = os.path.join(USER_HOME_DIR, '.lampsible')
#         ))
#         os.makedirs(private_data_dir)
#     except FileExistsError:
#         pass
# 
#     return os.path.abspath(private_data_dir)


# def init_project_dir(project_dir):
#     if project_dir == '':
#         return find_package_project_dir()
#     return project_dir

class Lampsible:

    def __init__(self):
        pass

    
    def set_runner_config(self, runner_config):
        self.runner_config = runner_config

    def ensure_ansible_galaxy_dependencies(self, galaxy_requirements_file):
        with open(galaxy_requirements_file, 'r') as stream:
            required_collections = []
            tmp_collections = safe_load(stream)['collections']
            for tmp_dict in tmp_collections:
                required_collections.append(tmp_dict['name'])

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
        missing_collections = []
        for required in required_collections:
            if required not in installed_collections:
                missing_collections.append(required)
        if len(missing_collections) == 0:
            return 0
        else:
            return install_galaxy_collections(missing_collections)



    def install_galaxy_collections(self, collections):
        ok_to_install = input("\nI have to download and install the following Ansible Galaxy dependencies into {}:\n- {}\nIs this OK (yes/no)? ".format(
            os.path.join(USER_HOME_DIR, '.ansible/'),
            '\n- '.join(collections)
        )).lower()
        while ok_to_install != 'yes' and ok_to_install != 'no':
            ok_to_install = input("Please type 'yes' or 'no': ")
        if ok_to_install == 'yes':
            print('\nInstalling Ansible Galaxy collections...')
            run_command(
                executable_cmd='ansible-galaxy',
                cmdline_args=['collection', 'install'] + collections,
            )
            print('\n... collections installed.')
            return 0
        else:
            print('Cannot run Ansible plays without Galaxy requirements. Aborting.')
            return 1
