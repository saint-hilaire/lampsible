DOCUMENTATION = r'''
    name: dynamic_inventory
    plugin_type: inventory
    short_description: Returns Ansible inventory from CLI args
    description: Returns Ansible inventory from CLI args
    options:
        web_host:
            description: Web server
            required: true
        web_user:
            description: Web server user
            required: true
        db_sys_host:
            description: Database server
            required: true
        db_sys_user:
            description: Database server user
            required: true
'''
from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):
    NAME = 'dynamic_inventory'

    def verify_file(self, path):
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        from pprint import pprint
        pprint(self.__dict__)

        self.inventory.add_group('web_servers')
        self.inventory.add_group('database_servers')

        self.inventory.add_host(
            self.get_option('web_host'),
            group='web_servers'
        )
        self.inventory.set_variable(
            self.get_option('web_host'),
            'ansible_user',
            self.get_option('web_user')
        )

        self.inventory.add_host(
            self.get_option('db_sys_host'),
            group='database_servers'
        )
        self.inventory.set_variable(
            self.get_option('db_sys_host'),
            'ansible_user',
            self.get_option('db_sys_user')
        )
        # Doesn't work because of different execution environment
        # import pdb; pdb.set_trace()
        # self.web_host = self.get_option('web_host')
        # print(self.web_host)
        # self.web_user = self.get_option('web_user')
        # self.db_sys_host = self.get_option('db_sys_host')
        # self.db_sys_user = self.get_option('db_sys_user')
        print('HELLO')

