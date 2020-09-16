# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmcgui
from resources.lib.fanarttv import FanartTV


class Script(object):
    def __init__(self):
        self.params = self.get_params()

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

    def manage_ftv_artwork(self, ftv_id=None, ftv_type=None):
        choice = xbmcgui.Dialog().contextmenu([
            'Select artwork',
            'Refresh all artwork'])
        if choice == -1:
            return
        if choice == 0:
            return FanartTV().select_artwork(ftv_id=ftv_id, ftv_type=ftv_type)
        if choice == 1:
            return FanartTV().refresh_all_artwork(ftv_id=ftv_id, ftv_type=ftv_type)

    def router(self):
        if not self.params:
            return
        if self.params.get('ftv_movie_artwork'):
            return self.manage_ftv_artwork(ftv_id=self.params.get('ftv_movie_artwork'), ftv_type='movies')
        if self.params.get('ftv_tv_artwork'):
            return self.manage_ftv_artwork(ftv_id=self.params.get('ftv_tv_artwork'), ftv_type='tv')
