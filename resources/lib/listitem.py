import xbmc
import xbmcgui
import resources.lib.utils as utils
import resources.lib.rpc as rpc
from resources.lib.plugin import ADDONPATH, PLUGINPATH


class ListItem(object):
    def __init__(
            self, label=None, label2=None, path=None, library=None, is_folder=True, params=None, next_page=None,
            parent_params=None, infolabels=None, infoproperties=None, art=None, cast=None,
            context_menu=None, stream_details=None, unique_ids=None,
            **kwargs):
        self.label = label or ''
        self.label2 = label2 or ''
        self.path = path or PLUGINPATH
        self.params = params or {}
        self.parent_params = parent_params or {}
        self.library = library or 'video'
        self.is_folder = is_folder
        self.infolabels = infolabels or {}
        self.infoproperties = infoproperties or {}
        self.art = art or {}
        self.cast = cast or []
        self.context_menu = context_menu or []
        self.stream_details = stream_details or {}
        self.unique_ids = unique_ids or {}
        self.set_as_next_page(next_page)

    def set_as_next_page(self, next_page=None):
        if not next_page:
            return
        self.label = xbmc.getLocalizedString(33078)
        self.art['thumb'] = '{}/resources/icons/tmdb/nextpage.png'.format(ADDONPATH)
        self.infoproperties['specialsort'] = 'bottom'
        self.params = self.parent_params.copy()
        self.params['page'] = next_page
        self.params.pop('update_listing', None)  # Just in case we updated the listing for search results
        self.path = PLUGINPATH
        self.is_folder = True

    def set_art_fallbacks(self):
        if not self.art.get('thumb'):
            self.art['thumb'] = '{}/resources/poster.png'.format(ADDONPATH)
        if not self.art.get('fanart'):
            self.art['fanart'] = '{}/fanart.jpg'.format(ADDONPATH)
        return self.art

    def set_art_from_fanarttv(self, fanarttv_api):
        if self.infolabels.get('mediatype') not in ['movie', 'tvshow', 'season', 'episode']:
            return
        if self.infolabels.get('mediatype') == 'movie':
            self.art = utils.merge_two_dicts(
                self.art, fanarttv_api.get_movie_allart(self.unique_ids.get('tmdb')))
        elif self.infolabels.get('mediatype') == ['tvshow', 'season', 'episode']:
            self.art = utils.merge_two_dicts(
                self.art, fanarttv_api.get_tv_allart(self.unique_ids.get('tvdb')))
        return self.art

    def _context_item_get_ftv_artwork(self):
        tmdb_type, uid = None, None
        if self.infolabels.get('mediatype') == 'movie':
            tmdb_type = 'movie'
            uid = self.unique_ids.get('tmdb')
        elif self.infolabels.get('mediatype') in ['tvshow', 'season', 'episode']:
            tmdb_type = 'tv'
            uid = self.unique_ids.get('tvdb')
        if tmdb_type and uid:
            return [(
                'Manage artwork',
                'RunScript(plugin.video.themoviedb.helper,ftv_{}_artwork={})'.format(tmdb_type, uid))]
        return []

    def set_standard_context_menu(self):
        self.context_menu += self._context_item_get_ftv_artwork()
        return self.context_menu

    def set_watched_from_trakt(self, sync_watched=None):
        if not sync_watched:
            return

        if self.infolabels.get('mediatype') not in ['movie', 'tvshow', 'season', 'episode']:
            return

        tmdb_id = self.unique_ids.get('tmdb')
        if self.infolabels.get('mediatype') in ['season', 'episode']:
            tmdb_id = self.infoproperties.get('tvshow.tmdb_id')

        sync_item = sync_watched.get(tmdb_id)
        if not sync_item:
            return

        if self.infolabels.get('mediatype') == 'movie':
            self.infolabels['playcount'] = utils.try_parse_int(sync_item.get('plays') or 1)
            self.infolabels['overlay'] = 5
            return

        if self.infolabels.get('mediatype') == 'tv':
            return  # TODO: Get tvshow watched count

        season = utils.try_parse_int(self.infolabels.get('season'))
        if not season:
            return
        if self.infolabels.get('mediatype') == 'season':
            return  # TODO: Get season watched count

        episode = utils.try_parse_int(self.infolabels.get('episode'))
        if not episode:
            return
        if self.infolabels.get('mediatype') == 'episode':
            for i in sync_item.get('seasons', []):
                if i.get('number', -1) == season:
                    for j in i.get('episodes', []):
                        if j.get('number', -1) == episode:
                            self.infolabels['playcount'] = utils.try_parse_int(j.get('plays') or 1)
                            self.infolabels['overlay'] = 5
                            return

    def get_kodi_dbid(self, kodi_db=None):
        if not kodi_db:
            return
        dbid = kodi_db.get_info(
            info='dbid',
            imdb_id=self.unique_ids.get('imdb'),
            tmdb_id=self.unique_ids.get('tmdb'),
            tvdb_id=self.unique_ids.get('tvdb'),
            originaltitle=self.infolabels.get('originaltitle'),
            title=self.infolabels.get('title'),
            year=self.infolabels.get('year'))
        return dbid

    def _get_kodi_details(self, dbid=None):
        if not dbid:
            return
        if self.infolabels.get('mediatype') == 'movie':
            return rpc.get_movie_details(dbid)
        elif self.infolabels.get('mediatype') == 'tv':
            return rpc.get_tvshow_details(dbid)
        # TODO: Add episode details need to also merge TV
        # elif self.infolabels.get('mediatype') == 'episode':
        #     return rpc.get_tvshow_details(dbid)

    def set_kodi_details(self, kodi_db=None, reverse=True):
        self.set_details(details=self._get_kodi_details(dbid=self.get_kodi_dbid(kodi_db=kodi_db)), reverse=reverse)

    def _convert_mediatype_to_tmdb(self, simplify_tv=True):
        if self.infolabels.get('mediatype') == 'movie':
            return 'movie'
        if self.infolabels.get('mediatype') == 'tvshow':
            return 'tv'
        if self.infolabels.get('mediatype') == 'season':
            return 'tv' if simplify_tv else 'season'
        if self.infolabels.get('mediatype') == 'episode':
            return 'tv' if simplify_tv else 'episode'

    def _get_tmdb_details(self, tmdb_api, cache_only=True):
        return tmdb_api.get_details(self._convert_mediatype_to_tmdb(), self.unique_ids.get('tmdb'), cache_only=cache_only)

    def set_tmdb_details(self, tmdb_api):
        self.set_details(details=self._get_tmdb_details(tmdb_api, cache_only=True))

    def set_details(self, details=None, reverse=False):
        if not details:
            return
        self.stream_details = utils.merge_two_dicts(details.get('streamdetails', {}), self.stream_details, reverse=reverse)
        self.infolabels = utils.merge_two_dicts(details.get('infolabels', {}), self.infolabels, reverse=reverse)
        self.infoproperties = utils.merge_two_dicts(details.get('infoproperties', {}), self.infoproperties, reverse=reverse)
        self.art = utils.merge_two_dicts(details.get('art', {}), self.art, reverse=reverse)
        self.unique_ids = utils.merge_two_dicts(details.get('unique_ids', {}), self.unique_ids, reverse=reverse)
        self.cast = self.cast or details.get('cast', [])

    def get_url(self):
        paramstring = '?{}'.format(utils.urlencode_params(**self.params)) if self.params else ''
        return '{}{}'.format(self.path, paramstring)

    def get_listitem(self):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2, path=self.get_url())
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs(self.unique_ids)
        listitem.setInfo(self.library, self.infolabels)
        listitem.setProperties(self.infoproperties)
        listitem.setArt(self.set_art_fallbacks())
        listitem.setCast(self.cast)
        listitem.addContextMenuItems(self.context_menu)

        if self.stream_details:
            for k, v in self.stream_details.items():
                if not k or not v:
                    continue
                for i in v:
                    if not i:
                        continue
                    listitem.addStreamInfo(k, i)

        return listitem
