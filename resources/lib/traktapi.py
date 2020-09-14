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
            force=False,
            login=False,
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
        self.dialog_noapikey_header = u'{0} {1} {2}'.format(self.addon.getLocalizedString(32007), self.req_api_name, self.addon.getLocalizedString(32011))
        self.dialog_noapikey_text = self.addon.getLocalizedString(32012)
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.headers = {'trakt-api-version': '2', 'trakt-api-key': self.client_id, 'Content-Type': 'application/json'}

        if force:
            self.login()
            return

        self.authorize(login)

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
            token = loads(self.addon.getSettingString('trakt_token')) or {}
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
                self.addon.setSettingString('trakt_token', '')
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
            self.addon.getLocalizedString(32097),
            self.addon.getLocalizedString(32096),
            self.addon.getLocalizedString(32095) + ': [B]' + self.code.get('user_code') + '[/B]')
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
        self.addon.setSettingString('trakt_token', dumps(self.authorization))
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

    def get_itemlist_sorted_cached(self, *args, page=1, limit=20, **kwargs):
        cache_refresh = True if page == 1 else False
        kwparams = {
            'cache_name': 'trakt.sortedlist.v4_0_0',
            'cache_days': 0.125,
            'cache_refresh': cache_refresh,
            'sortmethod': kwargs.pop('sortmethod', None),
            'sortdirection': kwargs.pop('sortdirection', None)}
        items = cache.use_cache(self.get_itemlist_sorted, *args, **kwparams)
        index_z = page * limit
        index_a = index_z - limit
        index_z = len(items) if len(items) < index_z else index_z
        return {'items': items[index_a:index_z], 'pagecount': -(-len(items) // limit)}
