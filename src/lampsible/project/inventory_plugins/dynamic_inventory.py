from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):
    NAME = 'dynamic_inventory'

    def verify_file(self, path):
        return True

    def parse(self, inventory, loader, path, cache=True):
        print('HELLO')
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        self.inventory.add_group('web_servers')
        self.inventory.add_group('database_servers')
        # Doesn't work because of different execution environment
        # import pdb; pdb.set_trace()
        self.web_host = self.get_option('web_host')
        print(self.web_host)
        self.web_user = self.get_option('web_user')
        self.db_sys_host = self.get_option('db_sys_host')
        self.db_sys_user = self.get_option('db_sys_user')

