import xbmcgui
import resources.lib.utils as utils


class ListItem(object):
    def __init__(
            self, label='', label2='', path='', library='video', is_folder=False, params={},
            infolabels={}, infoproperties={}, art={}, cast=[], contextmenu=[], streamdetails={}, uniqueids={},
            **kwargs):
        self.label = label
        self.label2 = label2
        self.path = path
        self.params = params
        self.library = library
        self.is_folder = is_folder
        self.infolabels = infolabels
        self.infoproperties = infoproperties
        self.art = art
        self.cast = cast
        self.contextmenu = contextmenu
        self.streamdetails = streamdetails
        self.uniqueids = uniqueids

    def get_url(self):
        paramstring = '?{}'.format(utils.urlencode_params(**self.params)) if self.params else ''
        return '{}{}'.format(self.path, paramstring)

    def get_listitem(self):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2, path=self.get_url())
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs(self.uniqueids)
        listitem.setInfo(self.library, self.infolabels)
        listitem.setProperties(self.infoproperties)
        listitem.setArt(self.art)
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
