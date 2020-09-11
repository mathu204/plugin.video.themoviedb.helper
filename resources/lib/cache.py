import datetime
import simplecache
_cache = simplecache.SimpleCache()
_cache_name = 'plugin.video.themoviedb.helper'


def get_cache(cache_name):
    return _cache.get(cache_name)


def set_cache(my_object, cache_name, cache_days=14):
    if my_object and cache_name and cache_days:
        _cache.set(cache_name, my_object, expiration=datetime.timedelta(days=cache_days))
    return my_object


def use_cache(func, *args, **kwargs):
    """
    Simplecache takes func with args and kwargs
    Returns the cached item if it exists otherwise does the function
    """
    cache_days = kwargs.pop('cache_days', 14)
    cache_name = kwargs.pop('cache_name', _cache_name)
    cache_only = kwargs.pop('cache_only', False)
    cache_refresh = kwargs.pop('cache_refresh', False)
    for arg in args:
        if arg:
            cache_name = u'{0}/{1}'.format(cache_name, arg)
    for key, value in kwargs.items():
        if value:
            cache_name = u'{0}&{1}={2}'.format(cache_name, key, value)
    my_cache = get_cache(cache_name) if not cache_refresh else None
    if my_cache:
        return my_cache
    elif not cache_only:
        my_object = func(*args, **kwargs)
        return set_cache(my_object, cache_name, cache_days)
