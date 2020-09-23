#!/usr/bin/env python
# -*- coding: utf-8 -*-
VALID_FILECHARS = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

LANGUAGES = [
    'ar-AE', 'ar-SA', 'be-BY', 'bg-BG', 'bn-BD', 'ca-ES', 'ch-GU', 'cs-CZ', 'da-DK', 'de-AT', 'de-CH',
    'de-DE', 'el-GR', 'en-AU', 'en-CA', 'en-GB', 'en-IE', 'en-NZ', 'en-US', 'eo-EO', 'es-ES', 'es-MX',
    'et-EE', 'eu-ES', 'fa-IR', 'fi-FI', 'fr-CA', 'fr-FR', 'gl-ES', 'he-IL', 'hi-IN', 'hu-HU', 'id-ID',
    'it-IT', 'ja-JP', 'ka-GE', 'kk-KZ', 'kn-IN', 'ko-KR', 'lt-LT', 'lv-LV', 'ml-IN', 'ms-MY', 'ms-SG',
    'nb-NO', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'si-LK', 'sk-SK', 'sl-SI',
    'sr-RS', 'sv-SE', 'ta-IN', 'te-IN', 'th-TH', 'tl-PH', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-HK',
    'zh-TW', 'zu-ZA']

PLAYERS_URLENCODE = [
    'name', 'showname', 'clearname', 'tvshowtitle', 'title', 'thumbnail', 'poster', 'fanart',
    'originaltitle', 'plot', 'cast', 'actors']

PLAYERS_BASEDIR_USER = 'special://profile/addon_data/plugin.video.themoviedb.helper/players/'

PLAYERS_BASEDIR_BUNDLED = 'special://home/addons/plugin.video.themoviedb.helper/resources/players/'

TMDB_BASIC_LISTS = {
    'popular': {
        'path': '{tmdb_type}/popular',
        'key': 'results'},
    'top_rated': {
        'path': '{tmdb_type}/top_rated',
        'key': 'results'},
    'upcoming': {
        'path': '{tmdb_type}/upcoming',
        'key': 'results'},
    'trending_day': {
        'path': 'trending/{tmdb_type}/day',
        'key': 'results'},
    'trending_week': {
        'path': 'trending/{tmdb_type}/week',
        'key': 'results'},
    'now_playing': {
        'path': '{tmdb_type}/now_playing',
        'key': 'results'},
    'airing_today': {
        'path': '{tmdb_type}/airing_today',
        'key': 'results'},
    'on_the_air': {
        'path': '{tmdb_type}/on_the_air',
        'key': 'results'},
    'recommendations': {
        'path': '{tmdb_type}/{tmdb_id}/recommendations',
        'key': 'results',
        'dbid_sorting': True},
    'similar': {
        'path': '{tmdb_type}/{tmdb_id}/similar',
        'key': 'results',
        'dbid_sorting': True},
    'stars_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'cast',
        'tmdb_type': 'movie',
        'dbid_sorting': True},
    'stars_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'cast',
        'dbid_sorting': True,
        'tmdb_type': 'tv'},
    'crew_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'crew',
        'dbid_sorting': True,
        'tmdb_type': 'movie'},
    'crew_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'crew',
        'dbid_sorting': True,
        'tmdb_type': 'tv'},
    'images': {
        'path': 'person/{tmdb_id}/images',
        'key': 'profiles',
        'tmdb_type': 'image'},
    'videos': {
        'path': '{tmdb_type}/{tmdb_id}/videos',
        'key': 'results',
        'tmdb_type': 'video'},
    'posters': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'posters',
        'tmdb_type': 'image'},
    'fanart': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'backdrops',
        'tmdb_type': 'image'},
    'movie_keywords': {
        'path': 'movie/{tmdb_id}/keywords',
        'key': 'keywords',
        'tmdb_type': 'keyword'},
    'reviews': {
        'path': '{tmdb_type}/{tmdb_id}/reviews',
        'key': 'results'}}
