import xbmc
import xbmcgui
import resources.lib.utils as utils
import resources.lib.plugin as plugin
import resources.lib.cache as cache
from resources.lib.requestapi import RequestAPI
from resources.lib.listitem import ListItem
from resources.lib.plugin import ADDON


API_URL = 'http://webservice.fanart.tv/v3'
ARTWORK_TYPES = {
    'movies': {
        'clearart': ['hdmovieclearart', 'movieclearart'],
        'clearlogo': ['hdmovielogo', 'movielogo'],
        'discart': ['moviedisc'],
        'poster': ['movieposter'],
        'fanart': ['moviebackground '],
        'landscape': ['moviethumb'],
        'banner': ['moviebanner']},
    'tv': {
        'clearart': ['hdclearart', 'clearart'],
        'clearlogo': ['hdtvlogo', 'clearlogo'],
        'characterart': ['characterart'],
        'poster': ['tvposter'],
        'fanart': ['showbackground '],
        'landscape': ['tvthumb'],
        'banner': ['tvbanner']}}


class FanartTV(RequestAPI):
    def __init__(
            self,
            api_key='fcca59bee130b70db37ee43e63f8d6c1',
            client_key=ADDON.getSettingString('fanarttv_clientkey'),
            language=plugin.get_language(),
            cache_short=ADDON.getSettingInt('cache_list_days'),
            cache_long=ADDON.getSettingInt('cache_details_days'),
            cache_only=False,
            cache_refresh=False):
        super(FanartTV, self).__init__(
            cache_short=cache_short,
            cache_long=cache_long,
            req_api_name='FanartTV',
            req_api_url=API_URL,
            req_api_key='api_key={}'.format(api_key))
        self.req_api_key = 'api_key={0}'.format(api_key) if api_key else self.req_api_key
        self.req_api_key = '{0}&client_key={1}'.format(self.req_api_key, client_key) if client_key else self.req_api_key
        self.language = language[:2] if language else 'en'
        self.cache_only = cache_only
        self.cache_refresh = cache_refresh

    def get_artwork_request(self, ftv_id, ftv_type):
        """
        ftv_type can be 'movies' 'tv'
        ftv_id is tmdb_id|imdb_id for movies and tvdb_id for tv
        """
        if not ftv_type or not ftv_id:
            return
        return self.get_request_lc(
            ftv_type, ftv_id,
            cache_force=1,  # Force the cache to save a dummy dict for 1 day so that we don't bother requesting 404s multiple times
            cache_fallback={},
            cache_only=self.cache_only,
            cache_refresh=self.cache_refresh)

    def _get_artwork_type(self, ftv_id, ftv_type, artwork_type):
        if not artwork_type:
            return
        response = self.get_artwork_request(ftv_id, ftv_type)
        if not response:
            return
        return response.get(artwork_type) or []

    def get_artwork_type(self, ftv_id, ftv_type, artwork_type):
        return cache.use_cache(
            self._get_artwork_type, ftv_id, ftv_type, artwork_type,
            cache_name='fanart_tv.type.{}.{}.{}.{}'.format(self.language, ftv_id, ftv_type, artwork_type),
            cache_only=self.cache_only)

    def _get_best_artwork(self, ftv_id, ftv_type, artwork_type):
        artwork = self.get_artwork_type(ftv_id, ftv_type, artwork_type)
        best_like = -1
        best_item = None
        for i in artwork:
            if i.get('lang', '') == self.language:
                return i.get('url', '')
            if (i.get('lang', '') == 'en' or not i.get('lang')) and i.get('likes', 0) > best_like:
                best_item = i.get('url', '')
                best_like = i.get('likes', 0)
        return best_item

    def get_best_artwork(self, ftv_id, ftv_type, artwork_type):
        return cache.use_cache(
            self._get_best_artwork, ftv_id, ftv_type, artwork_type,
            cache_name='fanart_tv.best.{}.{}.{}.{}'.format(self.language, ftv_id, ftv_type, artwork_type),
            cache_only=self.cache_only)

    def _get_artwork_func(self, ftv_id, ftv_type, artwork_type, get_list=False):
        func = self.get_best_artwork if not get_list else self.get_artwork_type
        return func(ftv_id, ftv_type, artwork_type)

    def get_movie_clearart(self, ftv_id, get_list=False):
        artwork = self._get_artwork_func(ftv_id, 'movies', 'hdmovieclearart', get_list=get_list)
        return artwork or self._get_artwork_func(ftv_id, 'movies', 'movieclearart', get_list=get_list)

    def get_movie_clearlogo(self, ftv_id, get_list=False):
        artwork = self._get_artwork_func(ftv_id, 'movies', 'hdmovielogo', get_list=get_list)
        return artwork or self._get_artwork_func(ftv_id, 'movies', 'movielogo', get_list=get_list)

    def get_movie_discart(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'movies', 'moviedisc', get_list=get_list)

    def get_movie_poster(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'movies', 'movieposter', get_list=get_list)

    def get_movie_fanart(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'movies', 'moviebackground', get_list=get_list)

    def get_movie_landscape(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'movies', 'moviethumb', get_list=get_list)

    def get_movie_banner(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'movies', 'moviebanner', get_list=get_list)

    def get_tv_clearart(self, ftv_id, get_list=False):
        artwork = self._get_artwork_func(ftv_id, 'tv', 'hdclearart', get_list=get_list)
        return artwork or self._get_artwork_func(ftv_id, 'tv', 'clearart', get_list=get_list)

    def get_tv_clearlogo(self, ftv_id, get_list=False):
        artwork = self._get_artwork_func(ftv_id, 'tv', 'hdtvlogo', get_list=get_list)
        return artwork or self._get_artwork_func(ftv_id, 'tv', 'clearlogo', get_list=get_list)

    def get_tv_banner(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'tv', 'tvbanner', get_list=get_list)

    def get_tv_landscape(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'tv', 'tvthumb', get_list=get_list)

    def get_tv_fanart(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'tv', 'showbackground', get_list=get_list)

    def get_tv_poster(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'tv', 'tvposter', get_list=get_list)

    def get_tv_characterart(self, ftv_id, get_list=False):
        return self._get_artwork_func(ftv_id, 'tv', 'characterart', get_list=get_list)

    def get_tv_allart(self, ftv_id):
        if self.get_artwork_request(ftv_id, 'tv'):  # Check we can get the request first so we don't re-ask eight times if it 404s
            return {
                'clearart': self.get_tv_clearart(ftv_id),
                'clearlogo': self.get_tv_clearlogo(ftv_id),
                'banner': self.get_tv_banner(ftv_id),
                'landscape': self.get_tv_landscape(ftv_id),
                'fanart': self.get_tv_fanart(ftv_id),
                'characterart': self.get_tv_characterart(ftv_id),
                'poster': self.get_tv_poster(ftv_id)}

    def get_movie_allart(self, ftv_id):
        if self.get_artwork_request(ftv_id, 'movies'):  # Check we can get the request first so we don't re-ask eight times if it 404s
            return {
                'clearart': self.get_movie_clearart(ftv_id),
                'clearlogo': self.get_movie_clearlogo(ftv_id),
                'banner': self.get_movie_banner(ftv_id),
                'landscape': self.get_movie_landscape(ftv_id),
                'fanart': self.get_movie_fanart(ftv_id),
                'poster': self.get_movie_poster(ftv_id),
                'discart': self.get_movie_discart(ftv_id)}

    # def get_tv_allart(self, ftv_id):
    #     if not ftv_id:
    #         return
    #     return cache.use_cache(
    #         self._get_tv_allart, ftv_id,
    #         cache_name='fanart_tv.tv.all.{}.{}'.format(self.language, ftv_id),
    #         cache_only=self.cache_only,
    #         cache_refresh=self.cache_refresh)

    # def get_movie_allart(self, ftv_id):
    #     if not ftv_id:
    #         return
    #     return cache.use_cache(
    #         self._get_movie_allart, ftv_id,
    #         cache_name='fanart_tv.movie.all.{}.{}'.format(self.language, ftv_id),
    #         cache_only=self.cache_only,
    #         cache_refresh=self.cache_refresh)

    def refresh_all_artwork(self, ftv_id=None, ftv_type=None, ok_dialog=True, container_refresh=True):
        self.cache_refresh = True
        with utils.busy_dialog():
            artwork = None
            if ftv_type == 'movies':
                artwork = self.get_movie_allart(ftv_id)
            elif ftv_type == 'tv':
                artwork = self.get_tv_allart(ftv_id)
        if ok_dialog and not artwork:
            xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))
        elif ok_dialog and artwork:
            xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32218).format(
                ftv_type, ftv_id, ', '.join([k.capitalize() for k, v in artwork.items() if v])))
        if artwork and container_refresh:
            xbmc.executebuiltin('Container.Refresh')
        return artwork

    def _get_artwork_selection(self, ftv_id, ftv_type, artwork_type, get_list=False):
        if ftv_type == 'movies' and artwork_type == 'clearart':
            return self.get_movie_clearart(ftv_id, get_list=get_list)
        if ftv_type == 'movies' and artwork_type == 'clearlogo':
            return self.get_movie_clearlogo(ftv_id, get_list=get_list)
        if ftv_type == 'movies' and artwork_type == 'banner':
            return self.get_movie_banner(ftv_id, get_list=get_list)
        if ftv_type == 'movies' and artwork_type == 'landscape':
            return self.get_movie_landscape(ftv_id, get_list=get_list)
        if ftv_type == 'movies' and artwork_type == 'fanart':
            return self.get_movie_fanart(ftv_id, get_list=get_list)
        if ftv_type == 'movies' and artwork_type == 'poster':
            return self.get_movie_poster(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'discart':
            return self.get_tv_discart(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'clearart':
            return self.get_tv_clearart(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'clearlogo':
            return self.get_tv_clearlogo(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'banner':
            return self.get_tv_banner(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'landscape':
            return self.get_tv_landscape(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'fanart':
            return self.get_tv_fanart(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'poster':
            return self.get_tv_poster(ftv_id, get_list=get_list)
        if ftv_type == 'tv' and artwork_type == 'characterart':
            return self.get_tv_characterart(ftv_id, get_list=get_list)

    def select_artwork(self, ftv_id=None, ftv_type=None, ok_dialog=True, container_refresh=True, blacklist=[]):
        if ftv_type not in ['movies', 'tv']:
            return
        with utils.busy_dialog():
            artwork = self.get_artwork_request(ftv_id, ftv_type)
        if ok_dialog and not artwork:
            xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))
        if not artwork:
            return

        # Choose Type
        _artwork_types = ['poster', 'fanart', 'clearart', 'clearlogo', 'landscape', 'banner']
        _artwork_types.append('discart' if ftv_type == 'movies' else 'characterart')
        artwork_types = [i for i in _artwork_types if i not in blacklist]  # Remove types that we previously looked for
        choice = xbmcgui.Dialog().select('Choose art', artwork_types)

        # User exited
        if choice == -1:
            return

        # Get artwork of user's choosing
        artwork_type = artwork_types[choice]
        artwork_items = self._get_artwork_selection(ftv_id, ftv_type, artwork_type, get_list=True)

        # If there was not artwork of that type found then blacklist it before re-prompting
        if not artwork_items:
            if ok_dialog:
                xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))
            blacklist.append(artwork_types[choice])
            return self.select_artwork(
                ftv_id=ftv_id, ftv_type=ftv_type, ok_dialog=ok_dialog,
                container_refresh=container_refresh, blacklist=blacklist)

        # Choose artwork from options
        items = [
            ListItem(
                label=i.get('url'),
                label2='Lang: {} | Likes: {} | ID: {}'.format(i.get('lang', ''), i.get('likes', 0), i.get('id', '')),
                art={'thumb': i.get('url')}).get_listitem() for i in artwork_items if i.get('url')]
        choice = xbmcgui.Dialog().select('Choose art', items, useDetails=True)

        # If user hits back go back to main menu rather than exit completely
        if choice == -1:
            return self.select_artwork(
                ftv_id=ftv_id, ftv_type=ftv_type, ok_dialog=ok_dialog,
                container_refresh=container_refresh, blacklist=blacklist)

        # Cache our choice as the best artwork forever since it was selected manually
        # Some types have have HD and SD variants so set cache for both
        for i in ARTWORK_TYPES.get(ftv_type, {}).get(artwork_type, []):
            success = cache.set_cache(
                artwork_items[choice].get('url'),
                cache_name='fanart_tv.best.{}.{}.{}.{}'.format(self.language, ftv_id, ftv_type, i),
                cache_days=10000)
        if success and container_refresh:
            xbmc.executebuiltin('Container.Refresh')
