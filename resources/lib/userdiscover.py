import xbmc
import xbmcgui
import resources.lib.cache as cache
import resources.lib.utils as utils
import resources.lib.plugin as plugin
from resources.lib.tmdb import TMDb
from resources.lib.plugin import ADDONPATH, ADDON


SORTBY_MOVIES = [
    'popularity.asc', 'popularity.desc', 'release_date.asc', 'release_date.desc', 'revenue.asc', 'revenue.desc',
    'primary_release_date.asc', 'primary_release_date.desc', 'original_title.asc', 'original_title.desc',
    'vote_average.asc', 'vote_average.desc', 'vote_count.asc', 'vote_count.desc']

SORTBY_TV = [
    'vote_average.desc', 'vote_average.asc', 'first_air_date.desc', 'first_air_date.asc',
    'popularity.desc', 'popularity.asc']


ALL_METHODS = [
    'open', 'with_separator', 'sort_by', 'add_rule', 'clear', 'save', 'with_cast', 'with_crew', 'with_people',
    'primary_release_year', 'primary_release_date.gte', 'primary_release_date.lte', 'release_date.gte', 'release_date.lte',
    'with_release_type', 'region', 'with_networks', 'air_date.gte', 'air_date.lte', 'first_air_date.gte',
    'first_air_date.lte', 'first_air_date_year', 'with_genres', 'without_genres', 'with_companies', 'with_keywords',
    'without_keywords', 'with_original_language', 'vote_count.gte', 'vote_count.lte', 'vote_average.gte',
    'vote_average.lte', 'with_runtime.gte', 'with_runtime.lte']


def _get_basedir_top(tmdb_type):
    return [
        {
            'label': ADDON.getLocalizedString(32238).format(plugin.convert_type(tmdb_type, plugin.TYPE_PLURAL)),
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'open'}
        },
        {
            'label': ADDON.getLocalizedString(32239),
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'with_separator'}
        },
        {
            'label': ADDON.getLocalizedString(32240),
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'sort_by'}
        }
    ]


def _get_basedir_add(tmdb_type):
    return [
        {
            'label': 'Add rule...',
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'add_rule'}
        },
        {
            'label': xbmc.getLocalizedString(192),
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'clear'}
        },
        {
            'label': xbmc.getLocalizedString(190),
            'art': {'thumb': '{}/resources/poster.png'.format(ADDONPATH)},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'save'}
        }
    ]


def _get_basedir_rules_movies():
    return [
        {'label': 'With Cast', 'method': 'with_cast'},
        {'label': 'With Crew', 'method': 'with_crew'},
        {'label': 'With People', 'method': 'with_people'},
        {'label': 'Primary Release Year', 'method': 'primary_release_year'},
        {'label': 'Primary Release Date After', 'method': 'primary_release_date.gte'},
        {'label': 'Primary Release Date Before', 'method': 'primary_release_date.lte'},
        {'label': 'Release Date After', 'method': 'release_date.gte'},
        {'label': 'Release Date Before', 'method': 'release_date.lte'},
        {'label': 'Release Type', 'method': 'with_release_type'},
        {'label': 'Release Region', 'method': 'region'}]


def _get_basedir_rules_tv():
    return [
        {'label': 'With Networks', 'method': 'with_networks'},
        {'label': 'Air Date After', 'method': 'air_date.gte'},
        {'label': 'Air Date Before', 'method': 'air_date.lte'},
        {'label': 'First Air Date After', 'method': 'first_air_date.gte'},
        {'label': 'First Air Date Before', 'method': 'first_air_date.lte'},
        {'label': 'First Air Year', 'method': 'first_air_date_year'}]


def _get_basedir_rules(tmdb_type):
    items = [
        {'label': 'With Genres', 'method': 'with_genres'},
        {'label': 'Without Genres', 'method': 'without_genres'},
        {'label': 'With Companies', 'method': 'with_companies'},
        {'label': 'With Keywords', 'method': 'with_keywords'},
        {'label': 'Without Keywords', 'method': 'without_keywords'}]
    items += _get_basedir_rules_movies() if tmdb_type == 'movie' else _get_basedir_rules_tv()
    items += [
        {'label': 'With Original Language', 'method': 'with_original_language'},
        {'label': 'Vote Count ( > or = )', 'method': 'vote_count.gte'},
        {'label': 'Vote Count ( < or = )', 'method': 'vote_count.lte'},
        {'label': 'Vote Average ( > or = )', 'method': 'vote_average.gte'},
        {'label': 'Vote Average ( < or = )', 'method': 'vote_average.lte'},
        {'label': 'Runtime (Minutes) ( > or = )', 'method': 'with_runtime.gte'},
        {'label': 'Runtime (Minutes) ( < or = )', 'method': 'with_runtime.lte'}]
    return items


def _get_basedir_new(tmdb_type, method):
    basedir_items = []
    for i in _get_basedir_rules(tmdb_type):
        item_method = i.pop('method', None)
        if _win_prop(item_method) or item_method == method:
            i['params'] = {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': item_method}
            basedir_items.append(i)
    return basedir_items


def _get_discover_params(tmdb_type):
    params = {'info': 'discover', 'tmdb_type': tmdb_type}
    rules = [{'method': 'with_separator'}, {'method': 'sort_by'}] + _get_basedir_rules(tmdb_type)
    for i in rules:
        item_method = i.pop('method', None)
        prop_method = _win_prop(item_method)
        if not prop_method:
            continue
        params[item_method] = prop_method
    return params


def _win_prop(name, prefix=None, **kwargs):
    prefix = 'TMDbHelper.UserDiscover.{}'.format(prefix) if prefix else 'TMDbHelper.UserDiscover'
    return utils.get_property(name, prefix=prefix, **kwargs)


def _clear_all_properties():
    for method in ALL_METHODS:
        _win_prop(method, clear_property=True)
        _win_prop(method, 'Label', clear_property=True)


def _get_affix(item_method, method, properties=None):
    if item_method == method:
        return properties.get('label') if properties else ''
    return _win_prop(item_method, 'Label')


def _get_formatted_item(item, method, properties=None):
    affix = _get_affix(item.get('params', {}).get('method'), method, properties)
    if affix:
        item['label'] = '{}: {}'.format(item.get('label'), affix)
    return item


def _get_sort_method(tmdb_type):
    sort_method_list = SORTBY_MOVIES if tmdb_type == 'movie' else SORTBY_TV
    sort_method = xbmcgui.Dialog().select(xbmc.getLocalizedString(39010), sort_method_list)
    if sort_method != -1:
        return {'value': sort_method_list[sort_method], 'label': sort_method_list[sort_method], 'method': 'sort_by'}


def _get_separator_method():
    if xbmcgui.Dialog().yesno(
            ADDON.getLocalizedString(32107), ADDON.getLocalizedString(32108),
            yeslabel=ADDON.getLocalizedString(32109), nolabel=ADDON.getLocalizedString(32110)):
        return {'value': 'OR', 'label': 'ANY', 'method': 'with_separator'}
    return {'value': 'AND', 'label': 'ALL', 'method': 'with_separator'}


def _get_selected_properties(data_list, header=None, multiselect=True):
    if not data_list:
        return
    header = header or ADDON.getLocalizedString(32111)
    func = xbmcgui.Dialog().multiselect if multiselect else xbmcgui.Dialog().select
    dialog_list = [i.get('name') for i in data_list]
    select_list = func(header, dialog_list)
    if not select_list:
        return
    if not multiselect:
        select_list = [select_list]
    labels, values = None, None
    for i in select_list:
        label = data_list[i].get('name')
        value = data_list[i].get('id')
        if not value:
            continue
        labels = '{0} / {1}'.format(labels, label) if labels else label
        values = '{0} / {1}'.format(values, value) if values else '{}'.format(value)
    if labels and values:
        return {'label': labels, 'value': values}


def _get_genre(tmdb_type):
    data_list = TMDb().get_request_lc('genre', tmdb_type, 'list')
    if data_list and data_list.get('genres'):
        return _get_selected_properties(data_list['genres'], header=ADDON.getLocalizedString(32112))


def _add_rule_method(label, method, tmdb_type):
    rules = None
    if '_genres' in method:
        rules = _get_genre(tmdb_type)
    if not rules:
        return
    rules['method'] = method
    return rules


def _add_rule(tmdb_type):
    rules = _get_basedir_rules(tmdb_type)
    x = xbmcgui.Dialog().select('Add Rule', [i.get('label') for i in rules])
    if x != -1:
        return _add_rule_method(rules[x].get('label'), rules[x].get('method'), tmdb_type)


class ListsUserDiscover():
    def list_discover(self, tmdb_type, **kwargs):
        items = TMDb().get_discover_list(tmdb_type, **kwargs)
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.library = plugin.convert_type(tmdb_type, plugin.TYPE_LIBRARY)
        self.container_content = plugin.convert_type(tmdb_type, plugin.TYPE_CONTAINER)
        return items

    def list_discoverdir_router(self, **kwargs):
        if kwargs.get('clear_cache') != 'True':
            return self.list_discoverdir(**kwargs)
        cache.set_search_history('discover', clear_cache=True)
        self.container_refresh = True

    def list_discoverdir(self, **kwargs):
        items = []
        params = utils.merge_two_dicts(kwargs, {'info': 'user_discover'})
        artwork = {'thumb': '{}/resources/poster.png'.format(ADDONPATH)}
        for i in ['movie', 'tv']:
            item = {
                'label': '{} {}'.format(ADDON.getLocalizedString(32174), plugin.convert_type(i, plugin.TYPE_PLURAL)),
                'params': utils.merge_two_dicts(params, {'tmdb_type': i}),
                'infoproperties': {'specialsort': 'top'},
                'art': artwork}
            items.append(item)

        history = cache.get_search_history('discover')
        history.reverse()
        for i in history:
            item = {
                'label': i.get('name'),
                'params': utils.merge_two_dicts(params, i.get('params', {})),
                'art': artwork}
            items.append(item)
        if history:
            item = {
                'label': ADDON.getLocalizedString(32237),
                'art': artwork,
                'params': utils.merge_two_dicts(params, {'info': 'dir_discover', 'clear_cache': 'True'})}
            items.append(item)
        return items

    def list_userdiscover(self, tmdb_type, **kwargs):
        method = kwargs.get('method')

        # Method routing
        properties = None
        if not method or method == 'clear':
            _clear_all_properties()
        elif method == 'sort_by':
            properties = _get_sort_method(tmdb_type)
        elif method == 'with_separator':
            properties = _get_separator_method()
        elif method == 'save':
            pass
        elif method == 'edit':
            pass
        else:
            properties = _add_rule(tmdb_type)

        method = properties.get('method') if properties else method

        # Set or clear property
        if properties and properties.get('value'):
            _win_prop(method, set_property=properties.get('value'))
            _win_prop(method, 'Label', set_property=properties.get('label'))
        else:
            _win_prop(method, clear_property=True)
            _win_prop(method, 'Label', clear_property=True)

        # Build directory items
        basedir_items = []
        basedir_items += _get_basedir_top(tmdb_type)
        basedir_items += _get_basedir_new(tmdb_type, method)
        basedir_items += _get_basedir_add(tmdb_type)

        items = [_get_formatted_item(i, method, properties) for i in basedir_items]
        items[0]['params'] = _get_discover_params(tmdb_type)
        self.update_listing = True if method else False
        return items
