import sys
import xbmcplugin
import resources.lib.utils as utils
import resources.lib.plugin as plugin
from resources.lib.listitem import ListItem


class Container(object):
    def __init__(self):
        self.handle = int(sys.argv[1])
        self.paramstring = utils.try_decode_string(sys.argv[2][1:])
        self.params = utils.parse_paramstring(sys.argv[2][1:])

    def add_items(self, items=None):
        for i in items:
            listitem = ListItem(**i)
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=listitem.get_url(),
                listitem=listitem.get_listitem(),
                isFolder=listitem.is_folder)

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)

    def list_basedir(self, info=None):
        items = plugin.get_basedir_items(info)
        self.add_items(items)
        self.finish_container()

    def router(self, endpoint=None):
        endpoint = endpoint or self.params.get('info')
        if endpoint == 'pass':
            return
        return self.list_basedir(endpoint)
