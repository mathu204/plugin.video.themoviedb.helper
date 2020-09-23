# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import resources.lib.utils as utils
import resources.lib.plugin as plugin
from resources.lib.fanarttv import FanartTV
from resources.lib.tmdb import TMDb
from resources.lib.plugin import ADDON, PLUGINPATH


class Script(object):
    def get_params(self):
        params = {}
        for arg in sys.argv:
            if arg == 'script.py':
                pass
            elif '=' in arg:
                arg_split = arg.split('=', 1)
                if arg_split[0] and arg_split[1]:
                    key, value = arg_split
                    value = value.strip('\'').strip('\"')
                    params.setdefault(key, value)
            else:
                params.setdefault(arg, True)
        return params

    def manage_artwork(self, ftv_id=None, ftv_type=None, **kwargs):
        if not ftv_id or not ftv_type:
            return
        choice = xbmcgui.Dialog().contextmenu([
            ADDON.getLocalizedString(32220),
            ADDON.getLocalizedString(32221)])
        if choice == -1:
            return
        if choice == 0:
            return FanartTV().select_artwork(ftv_id=ftv_id, ftv_type=ftv_type)
        if choice == 1:
            return FanartTV().refresh_all_artwork(ftv_id=ftv_id, ftv_type=ftv_type)

    def related_lists(self, tmdb_id=None, tmdb_type=None, season=None, episode=None, container_update=True, **kwargs):
        if not tmdb_id or not tmdb_type:
            return
        if tmdb_type == 'movie':
            items = [{'label': 'Play', 'path': PLUGINPATH, 'params': {
                'info': 'play', 'tmdb_id': tmdb_id, 'tmdb_type': tmdb_type}}]
            items += plugin.get_basedir_details('movie')
        elif tmdb_type == 'tv' and season is not None and episode is not None:
            items = [{'label': 'Play', 'path': PLUGINPATH, 'params': {
                'info': 'play', 'tmdb_id': tmdb_id, 'tmdb_type': tmdb_type, 'season': season, 'episode': episode}}]
            items += plugin.get_basedir_details('tv')
        elif tmdb_type == 'tv' and season is not None:
            items = [{'label': 'Browse', 'path': PLUGINPATH, 'params': {
                'info': 'episodes', 'tmdb_id': tmdb_id, 'tmdb_type': tmdb_type, 'season': season}}]
            items += plugin.get_basedir_details('tv')
        elif tmdb_type == 'tv':
            items = [{'label': 'Browse', 'path': PLUGINPATH, 'params': {
                'info': 'seasons', 'tmdb_id': tmdb_id, 'tmdb_type': tmdb_type}}]
            items += plugin.get_basedir_details('tv')
        elif tmdb_type == 'person':
            items = plugin.get_basedir_details('person')
        else:
            return
        choice = xbmcgui.Dialog().contextmenu([i.get('label') for i in items])
        if choice == -1:
            return
        item = items[choice]
        params = item.get('params')
        if not params:
            return
        item['params']['tmdb_id'] = tmdb_id
        item['params']['tmdb_type'] = tmdb_type
        if season is not None:
            item['params']['season'] = season
            if episode is not None:
                item['params']['episode'] = episode
        if not container_update:
            return item
        path = 'Container.Update({})' if xbmc.getCondVisibility("Window.IsMedia") else 'ActivateWindow(videos,{},return)'
        path = path.format(utils.get_url(path=item.get('path'), **item.get('params')))
        xbmc.executebuiltin(path)

    def refresh_details(self, tmdb_id=None, tmdb_type=None, season=None, episode=None, **kwargs):
        if not tmdb_id or not tmdb_type:
            return
        with utils.busy_dialog():
            details = TMDb().get_details(tmdb_type, tmdb_id, season=season, episode=episode)
        if details:
            xbmcgui.Dialog().ok('TMDbHelper', ADDON.getLocalizedString(32234).format(tmdb_type, tmdb_id))
            xbmc.executebuiltin('Container.Refresh')

    def router(self):
        self.params = self.get_params()
        if not self.params:
            return
        if self.params.get('manage_artwork'):
            return self.manage_artwork(**self.params)
        if self.params.get('refresh_details'):
            return self.refresh_details(**self.params)
        if self.params.get('related_lists'):
            return self.related_lists(**self.params)
