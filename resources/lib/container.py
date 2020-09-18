import sys
import xbmc
import xbmcgui
import xbmcplugin
import resources.lib.utils as utils
import resources.lib.cache as cache
import resources.lib.plugin as plugin
import resources.lib.constants as constants
import resources.lib.rpc as rpc
from resources.lib.listitem import ListItem
from resources.lib.tmdb import TMDb
from resources.lib.fanarttv import FanartTV
from resources.lib.itemutils import ItemUtils
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
        self.container_refresh = False
        self.kodi_db = None
        self.ftv_lookup = ADDON.getSettingBool('fanarttv_lookup')
        self.ftv_widget_lookup = ADDON.getSettingBool('widget_fanarttv_lookup')
        self.is_widget = True if self.params.get('widget') else False

    def add_items(self, items=None, allow_pagination=True, parent_params=None, kodi_db=None):
        if not items:
            return
        listitem_utils = ItemUtils(
            kodi_db=self.kodi_db,
            ftv_api=FanartTV(cache_only=self.ftv_is_cache_only(is_widget=self.is_widget)))
        listitem_utils.set_trakt_watched()
        for i in items:
            if not allow_pagination and 'next_page' in i:
                continue
            listitem = ListItem(parent_params=parent_params, **i)
            listitem.set_details(details=listitem_utils.get_tmdb_details(listitem))  # Quick because only get cached
            listitem.set_details(details=listitem_utils.get_ftv_details(listitem), reverse=True)  # Slow when not cache only
            listitem.set_details(details=listitem_utils.get_kodi_details(listitem), reverse=True)  # Quick because local db
            # listitem.set_details(details=listitem_utils.get_external_ids(listitem))  # Slow first time
            listitem.set_playcount(playcount=listitem_utils.get_playcount_from_trakt(listitem))  # Quick because of agressive caching of Trakt object and pre-emptive dict comprehension
            listitem.set_standard_context_menu()
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=listitem.get_url(),
                listitem=listitem.get_listitem(),
                isFolder=listitem.is_folder)

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)

    def ftv_is_cache_only(self, is_widget=False):
        if is_widget and self.ftv_widget_lookup:
            return False
        if not is_widget and self.ftv_lookup:
            return False
        return True

    def get_kodi_database(self, tmdb_type):
        if tmdb_type == 'movie':
            return rpc.KodiLibrary(dbtype='movie')
        if tmdb_type == 'tv':
            return rpc.KodiLibrary(dbtype='tvshow')

    def list_details(self, tmdb_type, tmdb_id=None, **kwargs):
        base_item = TMDb().get_details(tmdb_type, tmdb_id)
        items = []
        items.append(base_item)
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        return items

    def list_searchdir_router(self, tmdb_type, **kwargs):
        if kwargs.get('clear_cache') != 'True':
            return self.list_searchdir(tmdb_type, **kwargs)
        cache.set_search_history(tmdb_type, clear_cache=True)
        self.container_refresh = True

    def list_searchdir(self, tmdb_type, **kwargs):
        base_item = {
            'label': '{} {}'.format(xbmc.getLocalizedString(137), plugin.convert_type(tmdb_type, plugin.TYPE_PLURAL)),
            'art': {'thumb': '{}/resources/icons/tmdb/search.png'.format(ADDONPATH)},
            'infoproperties': {'specialsort': 'top'},
            'params': utils.merge_two_dicts(kwargs, {'info': 'search'})}
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

        items = TMDb().get_search_list(
            tmdb_type=tmdb_type, query=query, page=page,
            year=kwargs.get('year'),
            first_air_date_year=kwargs.get('first_air_date_year'),
            primary_release_year=kwargs.get('primary_release_year'))

        if not original_query:
            params = utils.merge_two_dicts(kwargs, {
                'info': 'search', 'type': tmdb_type, 'page': page, 'query': query,
                'update_listing': 'True'})
            self.container_update = '{}?{}'.format(PLUGINPATH, utils.urlencode_params(**params))
            # Trigger container update using new path with query after adding items
            # Prevents onback from re-prompting for user input by re-writing path

        self.update_listing = True if update_listing else False
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        self.kodi_db = self.get_kodi_database(tmdb_type)

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
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        return items

    def get_items_router(self, **kwargs):
        info = kwargs.get('info')
        if info == 'pass':
            return
        if info == 'dir_search':
            return self.list_searchdir_router(kwargs.get('type'), **kwargs)
        if info == 'search':
            return self.list_search(kwargs.get('type'), **kwargs)

        if kwargs.get('query') and not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = TMDb().get_tmdb_id(kwargs.get('type'), **kwargs)

        if info == 'details':
            return self.list_details(kwargs.get('type'), **kwargs)
        if info in constants.TMDB_BASIC_LISTS:
            return self.list_tmdb(kwargs.get('type'), **kwargs)
        return self.list_basedir(info)

    def get_directory(self):
        items = self.get_items_router(**self.params)
        if not items:
            return
        self.add_items(items, allow_pagination=self.allow_pagination, parent_params=self.params, kodi_db=self.kodi_db)
        self.finish_container(
            update_listing=self.update_listing,
            plugin_category=self.plugin_category,
            container_content=self.container_content)
        if self.container_update:
            xbmc.executebuiltin('Container.Update({})'.format(self.container_update))
        if self.container_refresh:
            xbmc.executebuiltin('Container.Refresh')
