import resources.lib.plugin as plugin
import resources.lib.utils as utils
from resources.lib.requestapi import RequestAPI
from resources.lib.plugin import ADDON, PLUGINPATH


IMAGEPATH_ORIGINAL = 'https://image.tmdb.org/t/p/original'
IMAGEPATH_POSTER = 'https://image.tmdb.org/t/p/w500'
API_URL = 'https://api.themoviedb.org/3'
TMDB_GENRE_IDS = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80, "Documentary": 99, "Drama": 18,
    "Family": 10751, "Fantasy": 14, "History": 36, "Horror": 27, "Kids": 10762, "Music": 10402, "Mystery": 9648,
    "News": 10763, "Reality": 10764, "Romance": 10749, "Science Fiction": 878, "Sci-Fi & Fantasy": 10765, "Soap": 10766,
    "Talk": 10767, "TV Movie": 10770, "Thriller": 53, "War": 10752, "War & Politics": 10768, "Western": 37}


class TMDb(RequestAPI):
    def __init__(
            self,
            api_key='a07324c669cac4d96789197134ce272b',
            language=plugin.get_language(),
            mpaa_prefix=plugin.get_mpaa_prefix(),
            cache_short=ADDON.getSettingInt('cache_list_days'),
            cache_long=ADDON.getSettingInt('cache_details_days')):
        super(TMDb, self).__init__(
            cache_short=cache_short,
            cache_long=cache_long,
            req_api_name='TMDb',
            req_api_url=API_URL,
            req_api_key='api_key={}'.format(api_key))
        self.iso_language = language[:2]
        self.iso_country = language[-2:]
        self.req_language = '{0}-{1}&include_image_language={0},null'.format(self.iso_language, self.iso_country)
        self.mpaa_prefix = mpaa_prefix

    def get_title(self, item):
        if item.get('title'):
            return item.get('title')
        elif item.get('name'):
            return item.get('name')
        elif item.get('author'):
            return item.get('author')
        elif item.get('width') and item.get('height'):
            return u'{0}x{1}'.format(item.get('width'), item.get('height'))

    def get_icon(self, item):
        if item.get('poster_path'):
            return self.get_imagepath(item.get('poster_path'), poster=True)
        elif item.get('profile_path'):
            return self.get_imagepath(item.get('profile_path'), poster=True)
        elif item.get('file_path'):
            return self.get_imagepath(item.get('file_path'))
        # TODO: Return fallback icon

    def get_poster(self, item):
        if item.get('poster_path'):
            return self.get_imagepath(item.get('poster_path'), poster=True)

    def get_fanart(self, item):
        if item.get('backdrop_path'):
            return self.get_imagepath(item.get('backdrop_path'))

    def get_imagepath(self, path_affix, poster=False):
        if poster:
            return '{}{}'.format(IMAGEPATH_POSTER, path_affix)
        return '{}{}'.format(IMAGEPATH_ORIGINAL, path_affix)

    def get_genre_by_id(self, genre_id):
        for k, v in TMDB_GENRE_IDS.items():
            if v == utils.try_parse_int(genre_id):
                return k

    def get_genres_by_id(self, genre_ids):
        genre_ids = genre_ids or []
        return [self.get_genre_by_id(genre_id) for genre_id in genre_ids if self.get_genre_by_id(genre_id)]

    def set_basic_infolabels(self, item, tmdb_type, infolabels=None):
        infolabels = infolabels or {}
        infolabels['title'] = self.get_title(item)
        infolabels['originaltitle'] = item.get('original_title')
        infolabels['mediatype'] = plugin.convert_type(tmdb_type, plugin.TYPE_DB)
        infolabels['rating'] = '{:0,.1f}'.format(utils.try_parse_float(item.get('vote_average')))
        infolabels['votes'] = '{:0,.0f}'.format(item.get('vote_count')) if item.get('vote_count') else None
        infolabels['plot'] = item.get('overview') or item.get('biography') or item.get('content')
        infolabels['premiered'] = item.get('air_date') or item.get('release_date') or item.get('first_air_date') or ''
        infolabels['year'] = infolabels.get('premiered')[:4]
        infolabels['genre'] = self.get_genres_by_id(item.get('genre_ids'))
        infolabels['country'] = item.get('origin_country')
        return infolabels

    def set_basic_art(self, item, art=None):
        art = art or {}
        art['thumb'] = self.get_icon(item)
        art['poster'] = self.get_poster(item)
        art['fanart'] = self.get_fanart(item)
        return art

    def set_unique_ids(self, item, unique_ids=None):
        unique_ids = unique_ids or {}
        unique_ids['tmdb'] = item.get('id')
        return unique_ids

    def set_basic_params(self, item, tmdb_type, params=None):
        params = params or {}
        params['info'] = 'details'
        params['type'] = tmdb_type
        params['tmdb_id'] = item.get('id')
        return params

    def set_basic_info(self, item, tmdb_type, base_item=None):
        base_item = base_item or {}
        base_item['label'] = self.get_title(item)
        base_item['art'] = self.set_basic_art(item)
        base_item['infolabels'] = self.set_basic_infolabels(item, tmdb_type)
        base_item['unique_ids'] = self.set_unique_ids(item)
        base_item['params'] = self.set_basic_params(item, tmdb_type)
        base_item['path'] = PLUGINPATH
        return base_item

    def get_basic_list(self, path, tmdb_type, page=None, key='results', **kwargs):
        response = self.request_list(path, page=page, **kwargs)
        results = response.get(key, []) if response else []
        items = [self.set_basic_info(i, tmdb_type) for i in results if i]
        if page and utils.try_parse_int(response.get('page', 0)) < utils.try_parse_int(response.get('total_pages', 0)):
            items.append({'next_page': utils.try_parse_int(response.get('page', 0)) + 1})
        return items

    def get_search_list(self, tmdb_type, query=None, page=None, **kwargs):
        return self.get_basic_list('search/{}'.format(tmdb_type), tmdb_type, page=page, key='results', query=query, **kwargs)

    def request_list(self, *args, **kwargs):
        return self.get_request_sc(*args, language=self.req_language, **kwargs)
