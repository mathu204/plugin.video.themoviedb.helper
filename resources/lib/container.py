import sys
import xbmc
import xbmcgui
import xbmcplugin
import resources.lib.utils as utils
import resources.lib.cache as cache
import resources.lib.plugin as plugin
import resources.lib.constants as constants
from resources.lib.listitem import ListItem
from resources.lib.tmdb import TMDb
from resources.lib.plugin import ADDONPATH, ADDON, PLUGINPATH


class Container(object):
    def __init__(self):
        self.handle = int(sys.argv[1])
        self.paramstring = utils.try_decode_string(sys.argv[2][1:])
        self.params = utils.parse_paramstring(sys.argv[2][1:])

    def add_items(self, items=None, url_info=None):
        if not items:
            return
        for i in items:
            listitem = ListItem(parent_params=self.params, **i)
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=listitem.get_url(),
                listitem=listitem.get_listitem(),
                isFolder=listitem.is_folder)

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)

    def list_searchdir(self, tmdb_type, clear_cache=False, **kwargs):
        cache.set_search_history(tmdb_type, clear_cache=True) if clear_cache else None
        update_listing = True if clear_cache else False
        base_item = {}
        base_item['label'] = '{} {}'.format(xbmc.getLocalizedString(137), plugin.convert_type(tmdb_type, plugin.TYPE_PLURAL))
        base_item['art'] = {'thumb': '{}/resources/icons/tmdb/search.png'.format(ADDONPATH)}
        base_item['params'] = kwargs.copy() or {}
        base_item['params']['info'] = 'search'
        items = []
        items.append(base_item)
        history = cache.get_search_history(tmdb_type)
        history.reverse()
        for i in history:
            item = {}
            item['label'] = i
            item['art'] = base_item.get('art')
            item['params'] = base_item.get('params').copy()
            item['params']['query'] = i
            items.append(item)
        if history:
            item = {}
            item['label'] = ADDON.getLocalizedString(32121)
            item['art'] = base_item.get('art')
            item['params'] = base_item.get('params').copy()
            item['params']['info'] = 'dir_search'
            item['params']['clear_cache'] = 'True'
            items.append(item)
        self.add_items(items)
        self.finish_container(update_listing=update_listing)

    def list_search(self, tmdb_type, query=None, update_listing=False, page=None, **kwargs):
        original_query = query
        query = query or cache.set_search_history(
            query=utils.try_decode_string(xbmcgui.Dialog().input(ADDON.getLocalizedString(32044), type=xbmcgui.INPUT_ALPHANUM)),
            tmdb_type=tmdb_type)
        if not query:
            return

        update_listing = True if update_listing else False
        self.add_items(TMDb().get_search_list(
            tmdb_type=tmdb_type, query=query, page=page,
            year=kwargs.get('year'),
            first_air_date_year=kwargs.get('first_air_date_year'),
            primary_release_year=kwargs.get('primary_release_year')))
        self.finish_container(
            container_content=plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER),
            update_listing=update_listing)

        if not original_query:
            params = kwargs.copy() if kwargs else {}
            params['info'] = 'search'
            params['type'] = tmdb_type
            params['page'] = page
            params['query'] = query
            params['update_listing'] = 'True'
            xbmc.executebuiltin('Container.Update({}?{})'.format(PLUGINPATH, utils.urlencode_params(**params)))

    def list_basedir(self, info=None):
        items = plugin.get_basedir_items(info)
        self.add_items(items)
        self.finish_container()

    def list_tmdb(self, tmdb_type, info=None, page=None, **kwargs):
        info_model = constants.TMDB_BASIC_LISTS.get(info)
        items = TMDb().get_basic_list(
            path=info_model.get('path', '').format(type=tmdb_type),
            tmdb_type=tmdb_type,
            key=info_model.get('key', 'results'),
            page=page)
        self.add_items(items)
        self.finish_container(container_content=plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER))

    def router(self):
        info = self.params.get('info')
        if info == 'pass':
            return
        if info == 'dir_search':
            return self.list_searchdir(self.params.get('type'), **self.params)
        if info == 'search':
            return self.list_search(self.params.get('type'), **self.params)
        if info in constants.TMDB_BASIC_LISTS:
            return self.list_tmdb(self.params.get('type'), **self.params)
        return self.list_basedir(info)
