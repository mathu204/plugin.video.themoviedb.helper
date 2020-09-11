import resources.lib.plugin as plugin
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

    def get_imagepath(self, path_affix, poster=False):
        if poster:
            return '{}{}'.format(IMAGEPATH_POSTER, path_affix)
        return '{}{}'.format(IMAGEPATH_ORIGINAL, path_affix)

    def request_list(self, *args, **kwargs):
        return self.get_request_sc(*args, language=self.req_language, **kwargs)

    def get_basic_list(self, info, tmdb_type, page=None):
        """ {tmdb_type}/{info} """
        response = self.request_list(tmdb_type, info, page=page)
        results = response.json().get('results', []) if response else []
        items = []
        for i in results:
            item = {}
            item['infolabels'] = {}
            item['art'] = {}
            item['label'] = item['infolabels']['title'] = i.get('title') or i.get('name')
            if i.get('poster_path'):
                item['art']['thumb'] = item['art']['poster'] = self.get_imagepath(i.get('poster_path'), poster=True)
            if i.get('backdrop_path'):
                item['art']['fanart'] = self.get_imagepath(i.get('backdrop_path'))
            items.append(item)
        return items
