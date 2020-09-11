import resources.lib.plugin as plugin
import resources.lib.utils as utils
from resources.lib.requestapi import RequestAPI
from resources.lib.plugin import ADDON


IMAGEPATH_ORIGINAL = 'https://image.tmdb.org/t/p/original'
IMAGEPATH_POSTER = 'https://image.tmdb.org/t/p/w500'
API_URL = 'https://api.themoviedb.org/3'


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

    def request_list(self, *args, **kwargs):
        return self.get_request_sc(*args, language=self.req_language, **kwargs)

    def get_basic_list(self, info, tmdb_type, page=None):
        """ {tmdb_type}/{info} """
        response = self.request_list(tmdb_type, info, page=page)
        results = response.get('results', []) if response else []
        items = []
        for i in results:
            item = {}
            item['art'] = {}
            item['infolabels'] = {}
            item['label'] = self.get_title(i)
            item['art']['thumb'] = self.get_icon(i)
            item['art']['poster'] = self.get_poster(i)
            item['art']['fanart'] = self.get_fanart(i)
            item['infolabels']['mediatype'] = plugin.convert_type(tmdb_type, 'dbtype')
            item['infolabels']['rating'] = '{:0,.1f}'.format(utils.try_parse_float(i.get('vote_average')))
            item['infolabels']['votes'] = '{:0,.0f}'.format(i.get('vote_count')) if i.get('vote_count') else None
            item['infolabels']['plot'] = i.get('overview') or i.get('biography') or i.get('content')
            item['infolabels']['premiered'] = i.get('air_date') or i.get('release_date') or i.get('first_air_date') or ''
            item['infolabels']['year'] = item['infolabels'].get('premiered')[:4]
            items.append(item)
        return items
