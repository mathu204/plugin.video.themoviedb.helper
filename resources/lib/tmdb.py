import resources.lib.plugin as plugin
import resources.lib.utils as utils
import resources.lib.cache as cache
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
APPEND_TO_RESPONSE = 'credits,images,release_dates,content_ratings,external_ids,videos,movie_credits,tv_credits'


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
        self.append_to_response = APPEND_TO_RESPONSE

    def get_tmdb_id(self, tmdb_type=None, imdb_id=None, tvdb_id=None, query=None, year=None, episode_year=None, **kwargs):
        func = self.get_request_sc
        if not tmdb_type:
            return
        request = None
        if tmdb_type == 'genre' and query:
            return TMDB_GENRE_IDS.get(query, '')
        elif imdb_id:
            request = func('find', imdb_id, language=self.req_language, external_source='imdb_id')
            request = request.get('{0}_results'.format(tmdb_type), [])
        elif tvdb_id:
            request = func('find', tvdb_id, language=self.req_language, external_source='tvdb_id')
            request = request.get('{0}_results'.format(tmdb_type), [])
        elif query:
            query = query.split(' (', 1)[0]  # Scrub added (Year) or other cruft in parentheses () added by Addons or TVDb
            if tmdb_type == 'tv':
                request = func('search', tmdb_type, language=self.req_language, query=query, first_air_date_year=year)
            else:
                request = func('search', tmdb_type, language=self.req_language, query=query, year=year)
            request = request.get('results', [])
        if not request:
            return
        if tmdb_type == 'tv' and episode_year and len(request) > 1:
            for i in sorted(request, key=lambda k: k.get('first_air_date', ''), reverse=True):
                if not i.get('first_air_date'):
                    continue
                if utils.try_parse_int(i.get('first_air_date', '9999')[:4]) <= utils.try_parse_int(episode_year):
                    if query in [i.get('name'), i.get('original_name')]:
                        return i.get('id')
        return request[0].get('id')

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

    def get_episode_infolabel(self, item):
        if item.get('episode_number'):
            return item.get('episode_number')
        if item.get('episode_count'):
            return item.get('episode_count')
        if item.get('seasons'):
            count = 0
            for i in item.get('seasons', []):
                count += utils.try_parse_int(i.get('episode_count', 0))
            return count

    def get_season_infolabel(self, item):
        if item.get('season_number'):
            return item.get('season_number')
        if item.get('season_count'):
            return item.get('season_count')
        if isinstance(item.get('seasons'), list):
            return len(item.get('seasons'))

    def get_basic_infolabels(self, item, item_type, infolabels=None):
        infolabels = infolabels or {}
        infolabels['title'] = self.get_title(item)
        infolabels['originaltitle'] = item.get('original_title')
        infolabels['mediatype'] = plugin.convert_type(item_type, plugin.TYPE_DB)
        infolabels['rating'] = '{:0,.1f}'.format(utils.try_parse_float(item.get('vote_average')))
        infolabels['votes'] = '{:0,.0f}'.format(item.get('vote_count')) if item.get('vote_count') else None
        infolabels['plot'] = item.get('overview') or item.get('biography') or item.get('content')
        infolabels['premiered'] = item.get('air_date') or item.get('release_date') or item.get('first_air_date') or ''
        infolabels['year'] = infolabels.get('premiered')[:4]
        infolabels['genre'] = self.get_genres_by_id(item.get('genre_ids'))
        infolabels['country'] = item.get('origin_country')
        infolabels['season'] = self.get_season_infolabel(item)
        infolabels['episode'] = self.get_episode_infolabel(item)
        return utils.del_empty_keys(infolabels, ['N/A', '0.0', '0'])

    def get_basic_infoproperties(self, item, tmdb_type, infoproperties=None):
        infoproperties = infoproperties or {}
        infoproperties['tmdb_type'] = tmdb_type
        infoproperties['tmdb_id'] = item.get('id')
        infoproperties['imdb_id'] = item.get('imdb_id') or item.get('external_ids', {}).get('imdb_id')
        infoproperties['tvdb_id'] = item.get('external_ids', {}).get('tvdb_id')
        return utils.del_empty_keys(infoproperties, ['N/A', '0.0', '0'])

    def get_basic_art(self, item, art=None):
        art = art or {}
        art['thumb'] = self.get_icon(item)
        art['poster'] = self.get_poster(item)
        art['fanart'] = self.get_fanart(item)
        return utils.del_empty_keys(art, ['N/A', '0.0', '0'])

    def get_unique_ids(self, item, unique_ids=None):
        unique_ids = unique_ids or {}
        unique_ids['tmdb'] = item.get('id')
        unique_ids['imdb'] = item.get('imdb_id') or item.get('external_ids', {}).get('imdb_id')
        unique_ids['tvdb'] = item.get('external_ids', {}).get('tvdb_id')
        return utils.del_empty_keys(unique_ids, ['N/A', '0.0', '0'])

    def get_basic_params(self, item, tmdb_type, params=None):
        params = params or {}
        params['info'] = 'details'
        params['tmdb_type'] = tmdb_type
        params['tmdb_id'] = item.get('id')
        return utils.del_empty_keys(params, ['N/A', '0.0', '0'])

    def get_basic_info(self, item, tmdb_type, base_item=None):
        base_item = base_item or {}
        if item and tmdb_type:
            base_item['label'] = self.get_title(item)
            base_item['art'] = self.get_basic_art(item)
            base_item['infolabels'] = self.get_basic_infolabels(item, tmdb_type)
            base_item['infoproperties'] = self.get_basic_infoproperties(item, tmdb_type)
            base_item['unique_ids'] = self.get_unique_ids(item)
            base_item['params'] = self.get_basic_params(item, tmdb_type)
            base_item['path'] = PLUGINPATH
        return base_item

    def get_trailer(self, item):
        if not isinstance(item, dict):
            return
        videos = item.get('videos') or {}
        videos = videos.get('results') or []
        for i in videos:
            if i.get('type', '') != 'Trailer' or i.get('site', '') != 'YouTube' or not i.get('key'):
                continue
            return 'plugin://plugin.video.youtube/play/?video_id={0}'.format(i.get('key'))

    def get_mpaa_rating(self, item):
        if not item.get('release_dates', {}) or not item.get('release_dates', {}).get('results'):
            return
        for i in item.get('release_dates').get('results'):
            if not i.get('iso_3166_1') or i.get('iso_3166_1') != self.iso_country:
                continue
            for i in sorted(i.get('release_dates', []), key=lambda k: k.get('type')):
                if i.get('certification'):
                    return '{0}{1}'.format(self.mpaa_prefix, i.get('certification'))

    def get_collection_name(self, item):
        if item.get('belongs_to_collection', {}) and item.get('belongs_to_collection', {}).get('name'):
            return item.get('belongs_to_collection', {}).get('name')

    def get_detailed_infolabels(self, item, tmdb_type, infolabels=None):
        infolabels = infolabels or {}
        infolabels['set'] = self.get_collection_name(item)
        infolabels['genre'] = utils.dict_to_list(item.get('genres', []), 'name')
        infolabels['imdbnumber'] = item.get('imdb_id') or item.get('external_ids', {}).get('imdb_id')
        infolabels['studio'] = utils.dict_to_list(item.get('production_companies', []), 'name')
        infolabels['country'] = utils.dict_to_list(item.get('production_countries', []), 'name')
        infolabels['duration'] = utils.try_parse_int(item.get('runtime', 0)) * 60
        infolabels['status'] = item.get('status')
        infolabels['tagline'] = item.get('tagline')
        infolabels['director'] = [i.get('name') for i in item.get('credits', {}).get('crew', []) if i.get('name') and i.get('job') == 'Director']
        infolabels['writer'] = [i.get('name') for i in item.get('credits', {}).get('crew', []) if i.get('name') and i.get('department') == 'Writing']
        infolabels['trailer'] = self.get_trailer(item)
        infolabels['mpaa'] = self.get_mpaa_rating(item)
        return utils.del_empty_keys(infolabels, ['N/A', '0.0', '0'])

    def get_detailed_info(self, item, tmdb_type, base_item=None):
        base_item = base_item or {}
        if item and tmdb_type:
            base_item = self.get_basic_info(item, tmdb_type, base_item)
            base_item['infolabels'] = self.get_detailed_infolabels(item, tmdb_type, base_item.get('infolabels', {}))
        return base_item

    def _get_details(self, tmdb_type, tmdb_id, season=None, episode=None, cache_only=False, cache_refresh=False):
        path_affix = []
        if season is not None:
            path_affix += ['season', season]
        if season is not None and episode is not None:
            path_affix += ['episode', episode]
        return self.get_request_lc(
            tmdb_type, tmdb_id, *path_affix,
            append_to_response=self.append_to_response,
            cache_only=cache_only, cache_refresh=cache_refresh) or {}

    def get_details(self, tmdb_type, tmdb_id, season=None, episode=None, cache_only=False, cache_refresh=False):
        if not tmdb_id or not tmdb_type:
            return
        details = cache.use_cache(
            self.get_detailed_info,
            item=self._get_details(tmdb_type, tmdb_id, cache_only=cache_only, cache_refresh=cache_refresh),
            tmdb_type=tmdb_type,
            cache_name='detailed.item.{}.{}.{}.{}'.format(tmdb_type, tmdb_id, None, None),
            cache_days=self.cache_long, cache_only=cache_only, cache_refresh=cache_refresh)
        if not details:
            return
        title = details.get('infolabels', {}).get('title')
        if season is not None:
            item = cache.use_cache(
                self.get_detailed_info,
                item=self._get_details(tmdb_type, tmdb_id, season, episode, cache_only, cache_refresh),
                tmdb_type='season' if episode is None else 'episode', base_item=details,
                cache_name='detailed.item.{}.{}.{}.{}'.format(tmdb_type, tmdb_id, season, episode),
                cache_days=self.cache_long, cache_only=cache_only, cache_refresh=cache_refresh)
            item['infolabels']['tvshowtitle'] = title
            item['unique_ids']['tmdb'] = tmdb_id
            item['params']['tmdb_id'] = tmdb_id
            item['params']['season'] = season
            item['params']['episode'] = episode
            return item
        return details

    def get_seasons(self, tmdb_id):
        request = self.get_request_sc('tv/{}'.format(tmdb_id))
        results = request.get('seasons', []) if request else []
        details = self.get_detailed_info(request, 'tv')
        items = []
        items_end = []
        for i in results:
            item = self.get_detailed_info(i, 'season', self.get_detailed_info(request, 'tv'))
            item['infolabels']['tvshowtitle'] = details.get('infolabels', {}).get('title')
            item['unique_ids']['tmdb'] = tmdb_id
            item['params']['tmdb_id'] = tmdb_id
            item['params']['season'] = i.get('season_number')
            items.append(item) if i.get('season_number') != 0 else items_end.append(item)
        return items + items_end

    def get_search_list(self, tmdb_type, **kwargs):
        """ standard kwargs: query= page= """
        kwargs['key'] = 'results'
        return self.get_basic_list('search/{}'.format(tmdb_type), tmdb_type, **kwargs)

    def get_basic_list(self, path, tmdb_type, key='results', **kwargs):
        response = self.get_request_sc(path, **kwargs)
        results = response.get(key, []) if response else []
        items = [self.get_basic_info(i, tmdb_type) for i in results if i]
        if utils.try_parse_int(response.get('page', 0)) < utils.try_parse_int(response.get('total_pages', 0)):
            items.append({'next_page': utils.try_parse_int(response.get('page', 0)) + 1})
        return items

    def get_request_sc(self, *args, **kwargs):
        """ Get API request using the short cache """
        kwargs['cache_days'] = self.cache_short
        kwargs['region'] = self.iso_country
        kwargs['language'] = self.req_language
        return self.get_request(*args, **kwargs)

    def get_request_lc(self, *args, **kwargs):
        """ Get API request using the long cache """
        kwargs['cache_days'] = self.cache_long
        kwargs['region'] = self.iso_country
        kwargs['language'] = self.req_language
        return self.get_request(*args, **kwargs)
