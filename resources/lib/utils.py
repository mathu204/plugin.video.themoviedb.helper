import sys
import xbmc
import time
from copy import copy
from resources.lib.plugin import ADDON
from contextlib import contextmanager
try:
    from urllib.parse import urlencode, unquote_plus  # Py3
except ImportError:
    from urllib import urlencode, unquote_plus


_addonlogname = '[plugin.video.themoviedb.helper]\n'
_debuglogging = ADDON.getSettingBool('debug_logging')


@contextmanager
def busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def kodi_log(value, level=0):
    try:
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        logvalue = u'{0}{1}'.format(_addonlogname, value)
        if sys.version_info < (3, 0):
            logvalue = logvalue.encode('utf-8', 'ignore')
        if level == 2 and _debuglogging:
            xbmc.log(logvalue, level=xbmc.LOGNOTICE)
        elif level == 1:
            xbmc.log(logvalue, level=xbmc.LOGNOTICE)
        else:
            xbmc.log(logvalue, level=xbmc.LOGDEBUG)
    except Exception as exc:
        xbmc.log(u'Logging Error: {}'.format(exc), level=xbmc.LOGNOTICE)


def try_parse_int(string, base=None):
    '''helper to parse int from string without erroring on empty or misformed string'''
    try:
        return int(string, base) if base else int(string)
    except Exception:
        return 0


def try_parse_float(string):
    '''helper to parse float from string without erroring on empty or misformed string'''
    try:
        return float(string or 0)
    except Exception:
        return 0


def try_decode_string(string, encoding='utf-8', errors=None):
    """helper to decode strings for PY 2 """
    if sys.version_info.major == 3:
        return string
    try:
        return string.decode(encoding, errors) if errors else string.decode(encoding)
    except Exception:
        return string


def try_encode_string(string, encoding='utf-8'):
    """helper to encode strings for PY 2 """
    if sys.version_info.major == 3:
        return string
    try:
        return string.encode(encoding)
    except Exception:
        return string


def parse_paramstring(paramstring):
    """ helper to assist with difference in urllib modules in PY2/3 """
    params = dict()
    paramstring = paramstring.replace('&amp;', '&')  # Just in case xml string
    for param in paramstring.split('&'):
        if '=' not in param:
            continue
        k, v = param.split('=')
        params[try_decode_string(unquote_plus(k))] = try_decode_string(unquote_plus(v))
    return params


def urlencode_params(*args, **kwargs):
    """ helper to assist with difference in urllib modules in PY2/3 """
    params = dict()
    for k, v in kwargs.items():
        params[try_encode_string(k)] = try_encode_string(v)
    return urlencode(params)


def get_timestamp(timestamp=None):
    if not timestamp:
        return
    if time.time() > timestamp:
        return
    return timestamp


def set_timestamp(wait_time=60):
    return time.time() + wait_time


def dictify(r, root=True):
    if root:
        return {r.tag: dictify(r, False)}
    d = copy(r.attrib)
    if r.text:
        d["_text"] = r.text
    for x in r.findall("./*"):
        if x.tag not in d:
            d[x.tag] = []
        d[x.tag].append(dictify(x, False))
    return d


def dict_to_list(items, key):
    return [i.get(key) for i in items if i.get(key)]


def merge_two_dicts(x, y, reverse=False):
    xx = y or {} if reverse else x or {}
    yy = x or {} if reverse else y or {}
    z = xx.copy()   # start with x's keys and values
    z.update(yy)    # modifies z with y's keys and values & returns None
    return z


def merge_two_dicts_deep(x, y, reverse=False):
    """ Deep merge y keys into copy of x """
    xx = y or {} if reverse else x or {}
    yy = x or {} if reverse else y or {}
    z = xx.copy()
    for k, v in yy.items():
        if isinstance(v, dict):
            merge_two_dicts_deep(z.setdefault(k, {}), v, reverse=reverse)
        elif v:
            z[k] = v
    return z


def del_empty_keys(d, values=[]):
    my_dict = d.copy()
    for k, v in d.items():
        if not v or v in values:
            del my_dict[k]
    return my_dict


def find_dict_in_list(list_of_dicts, key, value):
    return [list_index for list_index, dic in enumerate(list_of_dicts) if dic.get(key) == value]
