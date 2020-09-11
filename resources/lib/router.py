import sys
import resources.lib.utils as utils
import resources.lib.constants as constants


class Router(object):
    def __init__(self):
        self.handle = int(sys.argv[1])
        self.paramstring = utils.try_decode_string(sys.argv[2][1:])
        self.params = utils.parse_paramstring(sys.argv[2][1:])
        self.router(endpoint=self.params.get('info'))

    def list_basedir(self):
        pass

    def router(self, endpoint=None):
        if endpoint is None:
            self.list_basedir()
