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
        self.allow_pagination = True
        self.update_listing = False
        self.plugin_category = ''
        self.container_content = ''
        self.container_update = None

    def add_items(self, items=None, allow_pagination=True):
        if not items:
            return
        for i in items:
            if not allow_pagination and 'next_page' in i:
                continue
            listitem = ListItem(parent_params=self.params, **i)
            listitem.get_details()
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=listitem.get_url(),
                listitem=listitem.get_listitem(),
                isFolder=listitem.is_folder)

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)

    def list_details(self, tmdb_type, tmdb_id=None, **kwargs):
        base_item = TMDb().get_details(tmdb_type, tmdb_id)
        items = []
        items.append(base_item)
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        return items

    def list_searchdir_clear(self, tmdb_type):
        cache.set_search_history(tmdb_type, clear_cache=True)
        xbmc.executebuiltin('Container.Refresh')

    def list_searchdir(self, tmdb_type, clear_cache=False, **kwargs):
        if clear_cache:
            return self.list_searchdir_clear(tmdb_type)

        base_item = {
            'label': '{} {}'.format(xbmc.getLocalizedString(137), plugin.convert_type(tmdb_type, plugin.TYPE_PLURAL)),
            'art': {'thumb': '{}/resources/icons/tmdb/search.png'.format(ADDONPATH)},
            'params': utils.merge_two_dicts(kwargs or {}, {'info': 'search'})}
        items = []
        items.append(base_item)

        history = cache.get_search_history(tmdb_type)
        history.reverse()
        for i in history:
            item = {
                'label': i,
                'art': base_item.get('art'),
                'params': utils.merge_two_dicts(base_item.get('params', {}), {'query': i})}
            items.append(item)
        if history:
            item = {
                'label': ADDON.getLocalizedString(32121),
                'art': base_item.get('art'),
                'params': utils.merge_two_dicts(base_item.get('params', {}), {'info': 'dir_search', 'clear_cache': 'True'})}
            items.append(item)
        return items

    def list_search(self, tmdb_type, query=None, update_listing=False, page=None, **kwargs):
        original_query = query
        query = query or cache.set_search_history(
            query=utils.try_decode_string(xbmcgui.Dialog().input(ADDON.getLocalizedString(32044), type=xbmcgui.INPUT_ALPHANUM)),
            tmdb_type=tmdb_type)

        if not query:
            return

        self.update_listing = True if update_listing else False
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        items = TMDb().get_search_list(
            tmdb_type=tmdb_type, query=query, page=page,
            year=kwargs.get('year'),
            first_air_date_year=kwargs.get('first_air_date_year'),
            primary_release_year=kwargs.get('primary_release_year'))

        if not original_query:
            params = utils.merge_two_dicts(kwargs or {}, {
                'info': 'search', 'type': tmdb_type, 'page': page, 'query': query,
                'update_listing': 'True'})
            self.container_update = '{}?{}'.format(PLUGINPATH, utils.urlencode_params(**params))
            # Trigger container update using new path with query after adding items
            # Prevents onback from re-prompting for user input by re-writing path

        return items

    def list_basedir(self, info=None):
        return plugin.get_basedir_items(info)

    def list_tmdb(self, tmdb_type, info=None, tmdb_id=None, page=None, **kwargs):
        info_model = constants.TMDB_BASIC_LISTS.get(info)
        items = TMDb().get_basic_list(
            path=info_model.get('path', '').format(type=tmdb_type, tmdb_id=tmdb_id),
            tmdb_type=tmdb_type,
            key=info_model.get('key', 'results'),
            page=page)
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        return items

    def get_items_router(self):
        info = self.params.get('info')
        if info == 'pass':
            return
        if info == 'dir_search':
            return self.list_searchdir(self.params.get('type'), **self.params)
        if info == 'search':
            return self.list_search(self.params.get('type'), **self.params)

        if self.params.get('query') and not self.params.get('tmdb_id'):
            self.params['tmdb_id'] = TMDb().get_tmdb_id(self.params.get('type'), **self.params)

        if info == 'details':
            return self.list_details(self.params.get('type'), **self.params)
        if info in constants.TMDB_BASIC_LISTS:
            return self.list_tmdb(self.params.get('type'), **self.params)
        return self.list_basedir(info)

    def get_directory(self):
        items = self.get_items_router()
        if not items:
            return
        self.add_items(items, allow_pagination=self.allow_pagination)
        self.finish_container(
            update_listing=self.update_listing,
            plugin_category=self.plugin_category,
            container_content=self.container_content)
        if self.container_update:
            xbmc.executebuiltin('Container.Update({})'.format(self.container_update))
