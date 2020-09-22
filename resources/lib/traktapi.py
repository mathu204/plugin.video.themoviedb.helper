import xbmc
import xbmcgui
import random
import resources.lib.utils as utils
import resources.lib.cache as cache
from json import loads, dumps
from resources.lib.requestapi import RequestAPI
from resources.lib.plugin import ADDON


API_URL = 'https://api.trakt.tv/'
CLIENT_ID = 'e6fde6173adf3c6af8fd1b0694b9b84d7c519cefc24482310e1de06c6abe5467'
CLIENT_SECRET = '15119384341d9a61c751d8d515acbc0dd801001d4ebe85d3eef9885df80ee4d9'


class TraktAPI(RequestAPI):
    def __init__(
            self,
            cache_short=ADDON.getSettingInt('cache_list_days'),
            cache_long=ADDON.getSettingInt('cache_details_days')):
        super(TraktAPI, self).__init__(
            cache_short=cache_short,
            cache_long=cache_long,
            req_api_url=API_URL,
            req_api_name='Trakt')
        self.authorization = ''
        self.sync = {}
        self.last_activities = None
        self.prev_activities = None
        self.refresh_check = 0
        self.attempted_login = False
        self.dialog_noapikey_header = u'{0} {1} {2}'.format(ADDON.getLocalizedString(32007), self.req_api_name, ADDON.getLocalizedString(32011))
        self.dialog_noapikey_text = ADDON.getLocalizedString(32012)
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.headers = {'trakt-api-version': '2', 'trakt-api-key': self.client_id, 'Content-Type': 'application/json'}
        self.last_activities = {}
        self.sync_activities = {}
        self.authorize()

    def authorize(self, login=False):
        if self.authorization:
            return self.authorization
        token = self.get_stored_token()
        if token.get('access_token'):
            self.authorization = token
            self.headers['Authorization'] = 'Bearer {0}'.format(self.authorization.get('access_token'))
        elif login:
            if not self.attempted_login and xbmcgui.Dialog().yesno(
                    self.dialog_noapikey_header,
                    self.dialog_noapikey_text,
                    nolabel=xbmc.getLocalizedString(222),
                    yeslabel=xbmc.getLocalizedString(186)):
                self.login()
            self.attempted_login = True
        if self.authorization:
            xbmcgui.Window(10000).setProperty('TMDbHelper.TraktIsAuth', 'True')
        return self.authorization

    def get_stored_token(self):
        try:
            token = loads(ADDON.getSettingString('trakt_token')) or {}
        except Exception as exc:
            token = {}
            utils.kodi_log(exc, 1)
        return token

    def logout(self):
        token = self.get_stored_token()

        if not xbmcgui.Dialog().yesno(ADDON.getLocalizedString(32212), ADDON.getLocalizedString(32213)):
            return

        if token:
            response = self.get_api_request('https://api.trakt.tv/oauth/revoke', dictify=False, postdata={
                'token': token.get('access_token', ''),
                'client_id': self.client_id,
                'client_secret': self.client_secret})
            if response and response.status_code == 200:
                msg = ADDON.getLocalizedString(32216)
                ADDON.setSettingString('trakt_token', '')
            else:
                msg = ADDON.getLocalizedString(32215)
        else:
            msg = ADDON.getLocalizedString(32214)

        xbmcgui.Dialog().ok(ADDON.getLocalizedString(32212), msg)

    def login(self):
        self.code = self.get_api_request('https://api.trakt.tv/oauth/device/code', postdata={'client_id': self.client_id})
        if not self.code.get('user_code') or not self.code.get('device_code'):
            return  # TODO: DIALOG: Authentication Error
        self.progress = 0
        self.interval = self.code.get('interval', 5)
        self.expires_in = self.code.get('expires_in', 0)
        self.auth_dialog = xbmcgui.DialogProgress()
        self.auth_dialog.create(
            ADDON.getLocalizedString(32097),
            ADDON.getLocalizedString(32096),
            ADDON.getLocalizedString(32095) + ': [B]' + self.code.get('user_code') + '[/B]')
        self.poller()

    def refresh_token(self):
        if not self.authorization or not self.authorization.get('refresh_token'):
            self.login()
            return
        postdata = {
            'refresh_token': self.authorization.get('refresh_token'),
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'refresh_token'}
        self.authorization = self.get_api_request('https://api.trakt.tv/oauth/token', postdata=postdata)
        if not self.authorization or not self.authorization.get('access_token'):
            return
        self.on_authenticated(auth_dialog=False)

    def poller(self):
        if not self.on_poll():
            self.on_aborted()
            return
        if self.expires_in <= self.progress:
            self.on_expired()
            return
        self.authorization = self.get_api_request('https://api.trakt.tv/oauth/device/token', postdata={'code': self.code.get('device_code'), 'client_id': self.client_id, 'client_secret': self.client_secret})
        if self.authorization:
            self.on_authenticated()
            return
        xbmc.Monitor().waitForAbort(self.interval)
        if xbmc.Monitor().abortRequested():
            return
        self.poller()

    def on_aborted(self):
        """Triggered when device authentication was aborted"""
        utils.kodi_log(u'Trakt Authentication Aborted!', 1)
        self.auth_dialog.close()

    def on_expired(self):
        """Triggered when the device authentication code has expired"""
        utils.kodi_log(u'Trakt Authentication Expired!', 1)
        self.auth_dialog.close()

    def on_authenticated(self, auth_dialog=True):
        """Triggered when device authentication has been completed"""
        utils.kodi_log(u'Trakt Authenticated Successfully!', 1)
        ADDON.setSettingString('trakt_token', dumps(self.authorization))
        self.headers['Authorization'] = 'Bearer {0}'.format(self.authorization.get('access_token'))
        if auth_dialog:
            self.auth_dialog.close()

    def on_poll(self):
        """Triggered before each poll"""
        if self.auth_dialog.iscanceled():
            self.auth_dialog.close()
            return False
        else:
            self.progress += self.interval
            progress = (self.progress * 100) / self.expires_in
            self.auth_dialog.update(int(progress))
            return True

    def invalid_apikey(self):
        if self.refresh_check == 0:
            self.refresh_token()
        self.refresh_check += 1

    def get_response(self, *args, **kwargs):
        response = self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers)
        if self.refresh_check == 1:
            self.get_response(*args, **kwargs)
        return response

    def _sort_itemlist(self, items, sortmethod=None, sortdirection=None):
        reverse = True if sortdirection == 'desc' else False
        if sortmethod == 'rank':
            return sorted(items, key=lambda i: i.get('rank'), reverse=reverse)
        elif sortmethod == 'added':
            return sorted(items, key=lambda i: i['listed_at'], reverse=reverse)
        elif sortmethod == 'title':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('title'), reverse=reverse)
        elif sortmethod == 'released':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('first_aired') if i.get('type') == 'show' else i.get(i.get('type'), {}).get('released'), reverse=reverse)
        elif sortmethod == 'runtime':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('runtime'), reverse=reverse)
        elif sortmethod == 'popularity':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('comment_count'), reverse=reverse)
        elif sortmethod == 'percentage':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('rating'), reverse=reverse)
        elif sortmethod == 'votes':
            return sorted(items, key=lambda i: i.get(i.get('type'), {}).get('votes'), reverse=reverse)
        elif sortmethod == 'random':
            random.shuffle(items)
            return items
        return sorted(items, key=lambda i: i['listed_at'], reverse=True)

    def get_itemlist_sorted(self, *args, **kwargs):
        response = self.get_response(*args, extended='full')
        sortdirection = kwargs.get('sortdirection') or response.headers.get('X-Sort-How')
        sortmethod = kwargs.get('sortmethod') or response.headers.get('X-Sort-By')
        return self._sort_itemlist(response.json(), sortmethod=sortmethod, sortdirection=sortdirection)

    def get_itemlist_ranked(self, *args, **kwargs):
        response = self.get_response(*args)
        return sorted(response.json(), key=lambda i: i['rank'], reverse=False)

    def get_imdb_top250(self):
        return cache.use_cache(self.get_itemlist_ranked, 'users', 'nielsz', 'lists', 'active-imdb-top-250', 'items')

    def _get_id(self, id_type, unique_id, trakt_type=None, output_type=None):
        response = self.get_request_lc('search', id_type, unique_id, type=trakt_type)
        for i in response:
            if i.get('type') != trakt_type:
                continue
            if i.get(trakt_type, {}).get('ids', {}).get(id_type) != unique_id:
                continue
            if not output_type:
                return i.get(trakt_type, {}).get('ids', {})
            return i.get(trakt_type, {}).get('ids', {}).get(output_type)

    def get_id(self, id_type, unique_id, trakt_type=None, output_type=None):
        """
        trakt_type: movie, show, episode, person, list
        output_type: trakt, slug, imdb, tmdb, tvdb
        """
        cache.use_cache(
            self._get_id, id_type, unique_id, trakt_type=None, output_type=None,
            cache_name='trakt_get_id.{}.{}.{}.{}'.format(id_type, unique_id, trakt_type, output_type),
            cache_days=self.cache_long)

    def get_itemlist_sorted_cached(self, *args, **kwargs):
        page = kwargs.get('page') or 1
        limit = kwargs.get('limit') or 20
        cache_refresh = True if page == 1 else False
        kwparams = {
            'cache_name': 'trakt.sortedlist',
            'cache_days': 0.125,
            'cache_refresh': cache_refresh,
            'sortmethod': kwargs.pop('sortmethod', None),
            'sortdirection': kwargs.pop('sortdirection', None)}
        items = cache.use_cache(self.get_itemlist_sorted, *args, **kwparams)
        index_z = page * limit
        index_a = index_z - limit
        index_z = len(items) if len(items) < index_z else index_z
        return {'items': items[index_a:index_z], 'pagecount': -(-len(items) // limit)}

    def get_watched_progress(self, uid, hidden=False, specials=False, count_specials=False):
        if not self.authorize() or not uid:
            return
        last_activity = self._get_sync_refresh_status('show', 'watched_at')
        cache_refresh = True if last_activity else False
        return self.get_request_lc('shows/{}/progress/watched'.format(uid), cache_refresh=cache_refresh)

    def _get_activity(self, activities, trakt_type=None, activity_type=None):
        if not activities:
            return
        if not trakt_type:
            return activities.get('all', '')
        if not activity_type:
            return activities.get('{}s'.format(trakt_type), {})
        return activities.get('{}s'.format(trakt_type), {}).get(activity_type)

    def _set_activity(self, timestamp, trakt_type=None, activity_type=None):
        if not timestamp:
            return
        activities = cache.get_cache('sync_activity') or {}
        activities['all'] = timestamp
        if trakt_type and activity_type:
            activities['{}s'.format(trakt_type)] = activities.get('{}s'.format(trakt_type)) or {}
            activities['{}s'.format(trakt_type)][activity_type] = timestamp
        if not activities:
            return
        return cache.set_cache(activities, cache_name='sync_activity', cache_days=30)

    def _get_last_activity(self, trakt_type=None, activity_type=None):
        if not self.authorize():
            return
        if not self.last_activities:
            self.last_activities = self.get_request('sync/last_activities', cache_days=0.0007)  # Cache for approx 1 minute to prevent rapid recalls
        return self._get_activity(self.last_activities, trakt_type=trakt_type, activity_type=activity_type)

    def _get_sync_activity(self, trakt_type=None, activity_type=None):
        if not self.sync_activities:
            self.sync_activities = cache.get_cache('sync_activity')
        if not self.sync_activities:
            return
        return self._get_activity(self.sync_activities, trakt_type=trakt_type, activity_type=activity_type)

    def _get_sync_refresh_status(self, trakt_type=None, activity_type=None):
        last_activity = self._get_last_activity(trakt_type, activity_type)
        sync_activity = self._get_sync_activity(trakt_type, activity_type) if last_activity else None
        if not sync_activity or sync_activity != last_activity:
            return last_activity

    def _get_quick_list(self, response=None, trakt_type=None):
        if response and trakt_type:
            return {i.get(trakt_type, {}).get('ids', {}).get('tmdb'): i for i in response if i.get(trakt_type, {}).get('ids', {}).get('tmdb')}

    def _get_sync_list(self, path=None, trakt_type=None, activity_type=None, permissions=['movie', 'show'], quick_list=False):
        if not self.authorize():
            return
        if not trakt_type or not activity_type or not path:
            return
        if permissions and trakt_type not in permissions:
            return
        last_activity = self._get_sync_refresh_status(trakt_type, activity_type)
        cache_refresh = True if last_activity else False
        response = self.get_request_lc(path, cache_refresh=cache_refresh)
        if not response:
            return
        if last_activity:
            self._set_activity(last_activity, trakt_type=trakt_type, activity_type=activity_type)
        if not quick_list:
            return response
        return cache.use_cache(
            self._get_quick_list, response, trakt_type,
            cache_name='quick_list.{}'.format(path),
            cache_refresh=cache_refresh)

    def get_sync_watched(self, trakt_type, quick_list=False):
        return self._get_sync_list(
            path='sync/watched/{}s'.format(trakt_type),
            trakt_type=trakt_type,
            activity_type='watched_at',
            quick_list=quick_list)

    def get_sync_collection(self, trakt_type, quick_list=False):
        return self._get_sync_list(
            path='sync/collection/{}s'.format(trakt_type),
            trakt_type=trakt_type,
            activity_type='collected_at',
            quick_list=quick_list)
