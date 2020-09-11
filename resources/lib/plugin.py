#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon


ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')
ADDONPATH = ADDON.getAddonInfo('path')
PLUGINPATH = u'plugin://plugin.video.themoviedb.helper/'


def basedir_main():
    return [
        {
            'label': xbmc.getLocalizedString(342),
            'path': PLUGINPATH,
            'params': {'info': 'dir_movie'},
            'is_folder': True,
            'icon': '{}/resources/icons/tmdb/movies.png'.format(ADDONPATH)},
        {
            'label': xbmc.getLocalizedString(20343),
            'path': PLUGINPATH,
            'params': {'info': 'dir_tv'},
            'is_folder': True,
            'icon': '{}/resources/icons/tmdb/tv.png'.format(ADDONPATH)},
        {
            'label': ADDON.getLocalizedString(32172),
            'path': PLUGINPATH,
            'params': {'info': 'dir_person'},
            'is_folder': True,
            'icon': '{}/resources/icons/tmdb/cast.png'.format(ADDONPATH)},
        {
            'label': ADDON.getLocalizedString(32173),
            'path': PLUGINPATH,
            'params': {'info': 'dir_random'},
            'is_folder': True,
            'icon': '{}/resources/poster.png'.format(ADDONPATH)},
        {
            'label': ADDON.getLocalizedString(32174),
            'path': PLUGINPATH,
            'params': {'info': 'dir_discover'},
            'is_folder': True,
            'icon': '{}/resources/poster.png'.format(ADDONPATH)},
        {
            'label': 'TheMovieDb',
            'path': PLUGINPATH,
            'params': {'info': 'dir_tmdb'},
            'is_folder': True,
            'icon': '{}/resources/poster.png'.format(ADDONPATH)},
        {
            'label': 'Trakt',
            'path': PLUGINPATH,
            'params': {'info': 'dir_trakt'},
            'is_folder': True,
            'icon': '{}/resources/trakt.png'.format(ADDONPATH)}]
