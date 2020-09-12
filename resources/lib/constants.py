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

TMDB_BASIC_LISTS = {
    'search': {
        'path': 'search/{type}',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'popular': {
        'path': '{type}/popular',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'top_rated': {
        'path': '{type}/top_rated',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'upcoming': {
        'path': '{type}/upcoming',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'trending_day': {
        'path': 'trending/{type}/day',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'trending_week': {
        'path': 'trending/{type}/week',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'now_playing': {
        'path': '{type}/now_playing',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'airing_today': {
        'path': '{type}/airing_today',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'on_the_air': {
        'path': '{type}/on_the_air',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'}}
