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

BASEDIR_MAIN = [
    {
        'info': 'dir_movie',
        'name': 'Movies',
        'icon': '{0}/resources/icons/tmdb/movies.png'},
    {
        'info': 'dir_tv',
        'name': 'TV Shows',
        'icon': '{0}/resources/icons/tmdb/tv.png'},
    {
        'info': 'dir_person',
        'name': 'People',
        'icon': '{0}/resources/icons/tmdb/cast.png'},
    {
        'info': 'dir_random',
        'name': 'Randomised',
        'icon': '{0}/resources/poster.png'},
    {
        'info': 'dir_discover',
        'name': 'Discover',
        'icon': '{0}/resources/poster.png'},
    {
        'info': 'dir_tmdb',
        'name': 'TheMovieDb',
        'icon': '{0}/resources/poster.png'},
    {
        'info': 'dir_trakt',
        'name': 'Trakt',
        'icon': '{0}/resources/trakt.png'}]
