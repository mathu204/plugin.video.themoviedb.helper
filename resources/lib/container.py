import xbmcplugin
import resources.lib.utils as utils
from resources.lib.listitem import ListItem


class Container(object):
    def __init__(self, handle):
        self.handle = handle

    def add_items(self, items=None):
        for i in items:
            paramstring = '?{}'.format(utils.urlencode_params(**i.get('params'))) if i.get('params') else ''
            listitem = ListItem()
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url='{}{}'.format(i.get('path'), paramstring),
                listitem=listitem,
                isFolder=i.get('is_folder', False))

    def finish_container(self, update_listing=False, plugin_category=None, container_content=None):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)
