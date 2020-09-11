import xbmcgui


class ListItem(object):
    def __init__(self):
        self.label = None
        self.label2 = None
        self.path = None
        self.imdb_id = None
        self.tmdb_id = None
        self.library = None
        self.infolabels = {}
        self.infoproperties = {}
        self.art = {}
        self.cast = []
        self.contextmenu = []
        self.streamdetails = {}

    def set_listitem(self):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2, path=self.path)
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': self.tmdb_id})
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
