import resources.lib.plugin as plugin
import resources.lib.constants as constants
from resources.lib.traktapi import TraktAPI


class TraktLists():
    def list_trakt(self, info, tmdb_type, page=None, **kwargs):
        info_model = constants.TRAKT_BASIC_LISTS.get(info)
        info_tmdb_type = info_model.get('tmdb_type') or tmdb_type
        trakt_type = plugin.convert_type(tmdb_type, plugin.TYPE_TRAKT)
        items = TraktAPI().get_basic_list(
            path=info_model.get('path', '').format(trakt_type=trakt_type, **kwargs),
            item_key=info_model.get('item_key', '').format(trakt_type=trakt_type, **kwargs),
            trakt_type=trakt_type,
            params=info_model.get('params'),
            page=page or 1,
            authorize=info_model.get('authorize', False),
            paginate=info_model.get('paginate', False),
            sort_by=info_model.get('sort_by', None),
            sort_how=info_model.get('sort_how', None),
            extended=info_model.get('extended', None))
        self.tmdb_cache_only = False
        self.kodi_db = self.get_kodi_database(info_tmdb_type)
        self.library = plugin.convert_type(info_tmdb_type, plugin.TYPE_LIBRARY)
        self.container_content = plugin.convert_type(info_tmdb_type, plugin.TYPE_CONTAINER)
        return items
