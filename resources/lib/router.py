import sys
import resources.lib.utils as utils
import resources.lib.plugin as plugin
from resources.lib.container import Container


class Router(object):
    def __init__(self):
        self.handle = int(sys.argv[1])
        self.paramstring = utils.try_decode_string(sys.argv[2][1:])
        self.params = utils.parse_paramstring(sys.argv[2][1:])

    def run(self):
        self.router(endpoint=self.params.get('info'))

    def list_basedir(self, items=None):
        if not items:
            return
        container = Container(self.handle)
        container.add_items(items)

    def router(self, endpoint=None):
        if endpoint is None:
            self.list_basedir(plugin.basedir_main())
