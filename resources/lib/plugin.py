#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon


ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')
ADDONPATH = ADDON.getAddonInfo('path')
PLUGINPATH = u'plugin://plugin.video.themoviedb.helper/'


def convert_type(tmdb_type, output):
    if output == 'plural':
        if tmdb_type == 'movie':
            return xbmc.getLocalizedString(342)
        elif tmdb_type == 'tv':
            return xbmc.getLocalizedString(20343)
        elif tmdb_type == 'person':
            return ADDON.getLocalizedString(32172)
        elif tmdb_type == 'collection':
            return ADDON.getLocalizedString(32187)
        elif tmdb_type == 'review':
            return ADDON.getLocalizedString(32188)
        elif tmdb_type == 'keyword':
            return xbmc.getLocalizedString(21861)
        elif tmdb_type == 'network':
            return ADDON.getLocalizedString(32189)
        elif tmdb_type == 'studio':
            return ADDON.getLocalizedString(32190)
        elif tmdb_type == 'image':
            return ADDON.getLocalizedString(32191)
        elif tmdb_type == 'genre':
            return xbmc.getLocalizedString(135)
        elif tmdb_type == 'season':
            return xbmc.getLocalizedString(33054)
        elif tmdb_type == 'episode':
            return xbmc.getLocalizedString(20360)
        elif tmdb_type == 'video':
            return xbmc.getLocalizedString(10025)
    elif output == 'container':
        if tmdb_type == 'movie':
            return 'movies'
        elif tmdb_type == 'tv':
            return 'tvshows'
        elif tmdb_type == 'person':
            return 'actors'
        elif tmdb_type == 'collection':
            return 'sets'
        elif tmdb_type == 'image':
            return 'images'
        elif tmdb_type == 'genre':
            return 'genres'
        elif tmdb_type == 'season':
            return 'seasons'
        elif tmdb_type == 'episode':
            return 'episodes'
        elif tmdb_type == 'video':
            return 'videos'
    elif output == 'trakt':
        if tmdb_type == 'movie':
            return 'movie'
        elif tmdb_type == 'tv':
            return 'show'
        elif tmdb_type == 'season':
            return 'season'
        elif tmdb_type == 'episode':
            return 'episode'
    elif output == 'dbtype':
        if tmdb_type == 'movie':
            return 'movie'
        elif tmdb_type == 'tv':
            return 'tvshow'
        elif tmdb_type == 'person':
            return 'video'
        elif tmdb_type == 'collection':
            return 'set'
        elif tmdb_type == 'genre':
            return 'genre'
        elif tmdb_type == 'season':
            return 'season'
        elif tmdb_type == 'episode':
            return 'episode'
        elif tmdb_type == 'video':
            return 'video'
    return ''


def get_basedir_items(info=None):
    if not info:
        return basedir_main()
    if info == 'dir_movie':
        return get_basedir_list('movie', tmdb=True, trakt=True)
    if info == 'dir_tv':
        return get_basedir_list('tv', tmdb=True, trakt=True)
    if info == 'dir_person':
        return get_basedir_list('person', tmdb=True, trakt=True)
    if info == 'dir_tmdb':
        return get_basedir_list(None, tmdb=True)
    if info == 'dir_trakt':
        return get_basedir_list(None, trakt=True)


def get_basedir_list(item_type=None, trakt=False, tmdb=False):
    basedir = []
    if tmdb:
        basedir += basedir_tmdb()
    if trakt:
        basedir += basedir_trakt()

    items = []
    space = '' if item_type else ' '  # If only one type spaces are not needed for label because we dont add type name

    for i in basedir:
        for itype in i.get('types', []):
            if item_type and item_type != itype:
                continue
            plural = '' if item_type else convert_type(itype, 'plural')  # Dont add type name to label if only one type
            item = i.copy()
            item['label'] = i.get('label', '').format(space=space, item_type=plural)
            item['params']['type'] = itype
            item.pop('types', None)
            items.append(item)

    return items


def basedir_trakt():
    return [
        {
            'label': '{{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32192)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_collection'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/watchlist.png'.format(ADDONPATH)}},
        {
            'label': '{{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32193)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_watchlist'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/watchlist.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32194)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_history'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/recentlywatched.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32195)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_mostwatched'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/mostwatched.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32196)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_inprogress'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/inprogress.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32197),
            'types': ['tv'],
            'params': {'info': 'trakt_nextepisodes'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/inprogress.png'.format(ADDONPATH)}},
        {
            'label': '{{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32198)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_recommendations'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/recommended.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32199)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_becauseyouwatched'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/recommended.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32200)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_becausemostwatched'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/recommended.png'.format(ADDONPATH)}},
        {
            'label': '{} {{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32201), ADDON.getLocalizedString(32202)),
            'types': ['tv'],
            'params': {'info': 'trakt_myairing'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/airing.png'.format(ADDONPATH)}},
        {
            'label': '{} {{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32201), ADDON.getLocalizedString(32203)),
            'types': ['tv'],
            'params': {'info': 'trakt_calendar'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/calendar.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32204)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_trending'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/trend.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32175)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_popular'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/popular.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32205)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_mostplayed'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/mostplayed.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32206)),
            'types': ['movie', 'tv'],
            'params': {'info': 'trakt_anticipated'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/anticipated.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32207)),
            'types': ['movie'],
            'params': {'info': 'trakt_boxoffice'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/boxoffice.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32208),
            'types': ['both'],
            'params': {'info': 'trakt_trendinglists'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/trendinglist.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32209),
            'types': ['both'],
            'params': {'info': 'trakt_popularlists'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/popularlist.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32210),
            'types': ['both'],
            'params': {'info': 'trakt_likedlists'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/likedlist.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32211),
            'types': ['both'],
            'params': {'info': 'trakt_mylists'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/trakt/mylists.png'.format(ADDONPATH)}}]


def basedir_tmdb():
    return [
        {
            'label': '{}{{space}}{{item_type}}'.format(xbmc.getLocalizedString(137)),
            'types': ['movie', 'tv', 'person'],
            'params': {'info': 'dir_search'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/search.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32175)),
            'types': ['movie', 'tv', 'person'],
            'params': {'info': 'popular'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/popular.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32176)),
            'types': ['movie', 'tv'],
            'params': {'info': 'top_rated'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/toprated.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32177)),
            'types': ['movie'],
            'params': {'info': 'upcoming'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/upcoming.png'.format(ADDONPATH)}},
        {
            'label': '{{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32178)),
            'types': ['movie', 'tv', 'person'],
            'params': {'info': 'trending_day'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/upcoming.png'.format(ADDONPATH)}},
        {
            'label': '{{item_type}}{{space}}{}'.format(ADDON.getLocalizedString(32179)),
            'types': ['movie', 'tv', 'person'],
            'params': {'info': 'trending_week'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/upcoming.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32180),
            'types': ['movie'],
            'params': {'info': 'now_playing'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/intheatres.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32181),
            'types': ['tv'],
            'params': {'info': 'airing_today'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/airing.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32182),
            'types': ['tv'],
            'params': {'info': 'on_the_air'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/airing.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32183),
            'types': ['tv'],
            'params': {'info': 'library_nextaired'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/airing.png'.format(ADDONPATH)}},
        {
            'label': '{{item_type}}{{space}}{}'.format(xbmc.getLocalizedString(135)),
            'types': ['movie', 'tv'],
            'params': {'info': 'genres'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/genre.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32184)),
            'types': ['movie'],
            'params': {'info': 'revenue_movies'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32185)),
            'types': ['movie', 'tv'],
            'params': {'info': 'most_voted'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}},
        {
            'label': '{}{{space}}{{item_type}}'.format(ADDON.getLocalizedString(32186)),
            'types': ['movie', 'tv', 'person', 'collection', 'keyword', 'network', 'studio'],
            'params': {'info': 'all_items'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}}]


def basedir_main():
    return [
        {
            'label': xbmc.getLocalizedString(342),
            'params': {'info': 'dir_movie'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/movies.png'.format(ADDONPATH)}},
        {
            'label': xbmc.getLocalizedString(20343),
            'params': {'info': 'dir_tv'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/tv.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32172),
            'params': {'info': 'dir_person'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/icons/tmdb/cast.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32173),
            'params': {'info': 'dir_random'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}},
        {
            'label': ADDON.getLocalizedString(32174),
            'params': {'info': 'dir_discover'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}},
        {
            'label': 'TheMovieDb',
            'params': {'info': 'dir_tmdb'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}},
        {
            'label': 'Trakt',
            'params': {'info': 'dir_trakt'},
            'path': PLUGINPATH,
            'is_folder': True,
            'art': {'thumb': '{}/resources/trakt.png'.format(ADDONPATH)}}]
