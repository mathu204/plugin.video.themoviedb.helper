import xbmc
import xbmcgui
import resources.lib.utils as utils
from resources.lib.plugin import ADDONPATH, PLUGINPATH


class ListItem(object):
    def __init__(
            self, label=None, label2=None, path=None, library=None, is_folder=False, params=None, next_page=None, parent_params=None,
            infolabels=None, infoproperties=None, art=None, cast=None, contextmenu=None, streamdetails=None, uniqueids=None,
            **kwargs):
        self.label = label or ''
        self.label2 = label2 or ''
        self.path = path or ''
        self.params = params or {}
        self.parent_params = parent_params or {}
        self.library = library or 'video'
        self.is_folder = is_folder
        self.infolabels = infolabels or {}
        self.infoproperties = infoproperties or {}
        self.art = art or {}
        self.cast = cast or []
        self.contextmenu = contextmenu or []
        self.streamdetails = streamdetails or {}
        self.uniqueids = uniqueids or {}
        self.set_next_page(next_page) if next_page else None

    def set_next_page(self, next_page):
        self.label = xbmc.getLocalizedString(33078)
        self.art['thumb'] = '{}/resources/icons/tmdb/nextpage.png'.format(ADDONPATH)
        self.infolabels['mediatype'] = 'video'
        self.params = self.parent_params.copy()
        self.params['page'] = next_page
        self.path = PLUGINPATH

    def set_art_fallbacks(self):
        if not self.art.get('thumb'):
            self.art['thumb'] = '{}/resources/poster.png'.format(ADDONPATH)
        if not self.art.get('fanart'):
            self.art['fanart'] = '{}/fanart.jpg'.format(ADDONPATH)
        return self.art

    def get_url(self):
        paramstring = '?{}'.format(utils.urlencode_params(**self.params)) if self.params else ''
        return '{}{}'.format(self.path, paramstring)

    def get_listitem(self):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2, path=self.get_url())
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs(self.uniqueids)
        listitem.setInfo(self.library, self.infolabels)
        listitem.setProperties(self.infoproperties)
        listitem.setArt(self.set_art_fallbacks())
        listitem.setCast(self.cast)
        listitem.addContextMenuItems(self.contextmenu)

        if self.streamdetails:
            for k, v in self.streamdetails.items():
                if not k or not v:
                    continue
                for i in v:
                    if not i:
                        continue
                    listitem.addStreamInfo(k, i)

        return listitem
