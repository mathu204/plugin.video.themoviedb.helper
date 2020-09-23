import re
import sys
import xbmc
import xbmcgui
import xbmcaddon
import datetime
import resources.lib.rpc as rpc
import resources.lib.utils as utils
import resources.lib.constants as constants
from resources.lib.tmdb import TMDb
from resources.lib.listitem import ListItem
from resources.lib.plugin import ADDON, PLUGINPATH
from resources.lib.itemutils import ItemUtils
from json import loads, dumps
from string import Formatter
from collections import defaultdict
from threading import Thread
try:
    from urllib.parse import quote_plus, quote  # Py3
except ImportError:
    from urllib import quote_plus, quote  # Py2
if sys.version_info[0] >= 3:
    unicode = str  # In Py3 str is now unicode


def string_format_map(fmt, d):
    try:
        str.format_map
    except AttributeError:
        parts = Formatter().parse(fmt)
        return fmt.format(**{part[1]: d[part[1]] for part in parts})
    else:
        return fmt.format(**d)


class KeyboardInputter(Thread):
    def __init__(self, action=None, text=None, timeout=300):
        Thread.__init__(self)
        self.text = text
        self.action = action
        self.exit = False
        self.poll = 0.5
        self.timeout = timeout

    def run(self):
        while not xbmc.Monitor().abortRequested() and not self.exit and self.timeout > 0:
            xbmc.Monitor().waitForAbort(self.poll)
            self.timeout -= self.poll
            if self.text and xbmc.getCondVisibility("Window.IsVisible(DialogKeyboard.xml)"):
                rpc.get_jsonrpc("Input.SendText", {"text": self.text, "done": True})
                self.exit = True
            elif self.action and xbmc.getCondVisibility("Window.IsVisible(DialogSelect.xml) | Window.IsVisible(DialogConfirm.xml)"):
                rpc.get_jsonrpc(self.action)
                self.exit = True


class Players(object):
    def __init__(self, tmdb_type, tmdb_id=None, season=None, episode=None, **kwargs):
        with utils.busy_dialog():
            self.players = self._get_players_from_file()
            self.details = self._get_item_details(tmdb_type, tmdb_id, season, episode)
            self.item = self._get_detailed_item(tmdb_type, tmdb_id, season, episode)
            self.dialog_players = self._get_players_for_dialog(tmdb_type)
            self.is_folder = True
            self.is_local = False

    def _check_assert(self, keys=[]):
        if not self.item:
            return True  # No item so no need to assert values as we're only building to choose default player
        for i in keys:
            if i.startswith('!'):  # Inverted assert check for NOT value
                if self.item.get(i[1:]) and self.item.get(i[1:]) != 'None':
                    return False  # Key has a value so player fails assert check
            else:  # Standard assert check for value
                if not self.item.get(i) or self.item.get(i) == 'None':
                    return False  # Key didn't have a value so player fails assert check
        return True  # Player passed the assert check

    def _get_built_player(self, file, mode, value=None):
        name = ADDON.getLocalizedString(32061) if mode in ['play_movie', 'play_episode'] else xbmc.getLocalizedString(137)
        value = value or self.players.get(file) or {}
        return {
            'file': file, 'mode': mode,
            'name': '{} {}'.format(name, value.get('name')),
            'plugin_name': value.get('plugin'),
            'plugin_icon': value.get('icon') or xbmcaddon.Addon(value.get('plugin', '')).getAddonInfo('icon'),
            'fallback': value.get('fallback', {}).get(mode),
            'actions': value.get(mode)}

    def _get_players_for_dialog(self, tmdb_type):
        if tmdb_type not in ['movie', 'tv']:
            return []
        dialog_play, dialog_search = [], []
        for k, v in sorted(self.players.items(), key=lambda i: utils.try_parse_int(i[1].get('priority')) or 1000):
            if tmdb_type == 'movie':
                if v.get('play_movie') and self._check_assert(v.get('assert', {}).get('play_movie', [])):
                    dialog_play.append(self._get_built_player(file=k, mode='play_movie', value=v))
                if v.get('search_movie') and self._check_assert(v.get('assert', {}).get('search_movie', [])):
                    dialog_search.append(self._get_built_player(file=k, mode='search_movie', value=v))
            else:
                if v.get('play_episode') and self._check_assert(v.get('assert', {}).get('play_episode', [])):
                    dialog_play.append(self._get_built_player(file=k, mode='play_episode', value=v))
                if v.get('search_episode') and self._check_assert(v.get('assert', {}).get('search_episode', [])):
                    dialog_search.append(self._get_built_player(file=k, mode='search_episode', value=v))
        return dialog_play + dialog_search

    def _get_players_from_file(self):
        players = {}
        basedirs = [constants.PLAYERS_BASEDIR_USER]
        if ADDON.getSettingBool('bundled_players'):
            basedirs += [constants.PLAYERS_BASEDIR_BUNDLED]
        for basedir in basedirs:
            files = utils.get_files_in_folder(basedir, r'.*\.json')
            for file in files:
                meta = loads(utils.read_file(basedir + file)) or {}
                plugins = meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
                plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
                for i in plugins:
                    if not xbmc.getCondVisibility(u'System.HasAddon({0})'.format(i)):
                        break  # System doesn't have a required plugin so skip this player
                else:
                    players[file] = meta
        return players

    def _get_item_details(self, tmdb_type, tmdb_id, season=None, episode=None):
        details = TMDb().get_details(tmdb_type, tmdb_id, season, episode)
        if not details:
            return None
        details = ListItem(**details)
        details.infolabels['mediatype'] == 'movie' if tmdb_type == 'movie' else 'episode'
        details.set_details(details=ItemUtils().get_external_ids(details))
        return details

    def _get_detailed_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        details = self.details or self._get_item_details(tmdb_type, tmdb_id, season, episode)
        if not details:
            return None
        item = defaultdict(lambda: '+')
        item['id'] = item['tmdb'] = tmdb_id
        item['imdb'] = details.unique_ids.get('imdb')
        item['tvdb'] = details.unique_ids.get('tvdb')
        item['trakt'] = details.unique_ids.get('trakt')
        item['slug'] = details.unique_ids.get('slug')
        item['season'] = season
        item['episode'] = episode
        item['originaltitle'] = details.infolabels.get('originaltitle')
        item['title'] = details.infolabels.get('tvshowtitle') or details.infolabels.get('title')
        item['showname'] = item['clearname'] = item['tvshowtitle'] = item.get('title')
        item['year'] = details.infolabels.get('year')
        item['name'] = u'{} ({})'.format(item.get('title'), item.get('year'))
        item['premiered'] = item['firstaired'] = item['released'] = details.infolabels.get('premiered')
        item['plot'] = details.infolabels.get('plot')
        item['cast'] = item['actors'] = " / ".join([i.get('name') for i in details.cast if i.get('name')])
        item['thumbnail'] = details.art.get('thumb')
        item['poster'] = details.art.get('poster')
        item['fanart'] = details.art.get('fanart')
        item['now'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        if tmdb_type == 'tv' and season is not None and episode is not None:
            item['id'] = item.get('tvdb')
            item['title'] = details.infolabels.get('title')  # Set Episode Title
            item['name'] = u'{0} S{1:02d}E{2:02d}'.format(item.get('showname'), utils.try_parse_int(season), utils.try_parse_int(episode))
            item['season'] = season
            item['episode'] = episode
            item['showpremiered'] = details.infoproperties.get('tvshow.premiered')  # TODO: Add tvshow infoproperties in TMDb module
            item['showyear'] = details.infoproperties.get('tvshow.year')  # TODO: Add tvshow infoproperties in TMDb module
            # TODO: Add Episode IDs from Trakt - epid epimdb eptmdb eptrakt

        for k, v in item.copy().items():
            if k not in constants.PLAYERS_URLENCODE:
                continue
            v = u'{0}'.format(v)
            for key, value in {k: v, '{}_meta'.format(k): dumps(v)}.items():
                item[key] = value.replace(',', '')
                item[key + '_+'] = value.replace(',', '').replace(' ', '+')
                item[key + '_-'] = value.replace(',', '').replace(' ', '-')
                item[key + '_escaped'] = quote(quote(utils.try_encode_string(value)))
                item[key + '_escaped+'] = quote(quote_plus(utils.try_encode_string(value)))
                item[key + '_url'] = quote(utils.try_encode_string(value))
                item[key + '_url+'] = quote_plus(utils.try_encode_string(value))
        return item

    def _select_player(self, detailed=True):
        """ Returns user selected player via dialog - detailed bool switches dialog style """
        players = [ListItem(
            label=i.get('name'),
            label2='{} v{}'.format(i.get('plugin_name'), xbmcaddon.Addon(i.get('plugin_name', '')).getAddonInfo('version')),
            art={'thumb': i.get('plugin_icon')}).get_listitem() for i in self.dialog_players]
        x = xbmcgui.Dialog().select(ADDON.getLocalizedString(32042), players, useDetails=detailed)
        if x == -1:
            return {}
        player = self.dialog_players[x]
        player['idx'] = x
        return player

    def _get_player_fallback(self, fallback):
        if not fallback:
            return
        file, mode = fallback.split()
        if not file or not mode:
            return
        player = self._get_built_player(file, mode)
        if not player:
            return
        for x, i in enumerate(self.dialog_players):
            if i == player:
                player['idx'] = x
                return player

    def _get_path_from_rules(self, folder, action):
        for x, f in enumerate(folder):
            for k, v in action.items():  # Iterate through our key (infolabel) / value (infolabel must match) pairs of our action
                if k == 'position':  # We're looking for an item position not an infolabel
                    if utils.try_parse_int(string_format_map(v, self.item)) != x + 1:  # Format our position value and add one since people are dumb and don't know that arrays start at 0
                        break  # Not the item position we want so let's go to next item in folder
                elif not f.get(k) or not re.match(string_format_map(v, self.item), u'{}'.format(f.get(k, ''))):  # Format our value and check if it regex matches the infolabel key
                    break  # Item's key value doesn't match value we are looking for so let's got to next item in folder
            else:  # Item matched our criteria so let's return it
                if f.get('file'):
                    if f.get('filetype') == 'file':
                        self.is_folder = False  # Set false for files so we can play
                    return f.get('file')  # Get ListItem.FolderPath for item and return as player

    def _get_path_from_actions(self, actions):
        keyboard_input = None
        path = actions[0]
        for action in actions[1:]:
            # Check if we've got a playable item already
            if not self.is_folder:
                return path

            # Start thread with keyboard inputter if needed
            if action.get('keyboard'):
                if action.get('keyboard') in ['Up', 'Down', 'Left', 'Right', 'Select']:
                    keyboard_input = KeyboardInputter(action="Input.{}".format(action.get('keyboard')))
                else:
                    keyboard_input = KeyboardInputter(text=string_format_map(action.get('keyboard', ''), self.item))
                keyboard_input.setName('keyboard_input')
                keyboard_input.start()
                continue  # Go to next action

            # Get the next folder from the plugin
            with utils.busy_dialog():
                folder = rpc.get_directory(string_format_map(path, self.item))

            # Kill our keyboard inputter thread
            if keyboard_input:
                keyboard_input.exit = True
                keyboard_input = None

            # Special option to show dialog of items to select from TODO!!
            if action.get('dialog'):
                auto = True if action.get('dialog', '').lower() == 'auto' else False
                return self.player_dialogselect(folder, auto=auto)

            # Apply the rules for the current action and grab the path
            path = self._get_path_from_rules(folder, action)
            if not path:
                return
        return path

    def _get_path_from_player(self, player=None):
        if not player or not isinstance(player, dict):
            return
        actions = player.get('actions')
        if not actions:
            return
        if isinstance(actions, list):
            return self._get_path_from_actions(actions)
        if isinstance(actions, unicode) or isinstance(actions, str):
            return string_format_map(actions, self.item)  # Single path so return it formatted

    def _get_resolved_path(self, player=None):
        path = None
        player = player or self._select_player()
        if not player:
            return
        path = self._get_path_from_player(player)
        if not path:
            if player.get('idx') is not None:
                del self.dialog_players[player['idx']]  # Remove out player so we don't re-ask user for it
            fallback = self._get_player_fallback(player['fallback']) if player.get('fallback') else None
            return self._get_resolved_path(fallback)
        return path

    def get_resolved_path(self, return_listitem=True):
        if not self.item:
            return
        xbmcgui.Window(10000).clearProperty('TMDbHelper.PlayerInfoString')
        path = self._get_resolved_path()
        if return_listitem:
            self.details.path = path
            self.details.params = {}
            path = self.details.get_listitem()
        return path

    def play(self):
        # Get some info about current container for container update hack
        folder_path = xbmc.getInfoLabel("Container.FolderPath")
        current_pos = xbmc.getInfoLabel("Container.CurrentItem")
        containerid = xbmc.getInfoLabel("System.CurrentControlID")

        # Get the resoved path
        listitem = self.get_resolved_path()
        path = listitem.getPath()

        # Some plugins use container.update after search results to rewrite path history
        # This is a quick hack to rewrite the path back to our original path
        if folder_path and xbmc.getInfoLabel("Container.FolderPath") != folder_path:
            xbmc.executebuiltin('Container.Update({}&update_listing=true)'.format(folder_path))
            xbmc.executebuiltin('SetFocus({},{},absolute)'.format(containerid, current_pos))

        # Check we have an actual path to open
        if not path or path == PLUGINPATH:
            return

        # Kodi DB and strm files need to play with PlayMedia() to resolve properly
        # PlayMedia() will crash Kodi if external addon doesn't resolve directly to playable file so send to player instead
        # Returning path to Container and using setResolvedUrl is also not possible because external addon might not resolve
        # Not sure if method exists to determine if path returned from JSON RPC will be a resolvable one?
        # Maybe the isPlayable property flag can be checked?
        action = None
        if not self.is_folder and (self.is_local or path.endswith('.strm')):
            action = u'PlayMedia(\"{0}\")'.format(path)
        elif self.is_folder and xbmc.getCondVisibility("Window.IsMedia"):
            action = u'Container.Update({0})'.format(path)
        elif self.is_folder:
            action = u'ActivateWindow(videos,{0},return)'.format(path)
        if action:
            xbmc.executebuiltin(utils.try_encode_string(utils.try_decode_string(action)))
        elif not self.is_folder:
            xbmc.Player().play(path, listitem)

        return path
