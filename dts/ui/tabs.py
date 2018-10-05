import wx
import wx.lib.agw.aui as aui

import dts
from dts.ui.panels.channeleditor import ChannelEditorPanel
import logging as log


class Notebook(aui.AuiNotebook):
    """
    This class functions as the base for both the left and right tab notebooks of the GUI
    Documentation for base class:
    - http://xoomer.virgilio.it/infinity77/AGW_Docs/aui.auibook.AuiNotebook.html
    """
    def __init__(self, parent, id=wx.ID_ANY):
        style = aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_NO_TAB_FOCUS
        aui.AuiNotebook.__init__(self, parent, id, agwStyle=style)

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)

        dts.ui.tabset = self

    def AddPage(self, page, label, select=True):
        aui.AuiNotebook.AddPage(self, page, label, select=False)
        log.info("Page added: {0}".format(page.__class__.__name__))
        if select:
            i = self.GetPageIndex(page)
            self.SetSelection(i, force=True)

    def GetPages(self):
        pass

    def DeletePage(self, page_idx):
        """Subclasses the parent notebook method in order to prevent deletion of new tab selector tab."""
        page = self.GetPage(page_idx)
        if "NewPanelSelector" in page.__class__.__name__:
            log.error("Can't delete this page")
        else:
            aui.AuiNotebook.DeletePage(self, page_idx)

    def on_page_changed(self, evt):
        id = evt.GetSelection()
        newPage = self.GetPage(id)
        log.info("Page changed: {0}".format(newPage.__class__.__name__))
        self.current_page_id = id
        self.update_active_main(newPage)
        self.window.update_menu_bar()

        try:
            self.window.status.set_current_channel(newPage.data.get_channel())
            self.window.status.set_current_subset(newPage.data)
        except AttributeError:
            pass

        try:
            self.window.status.set_current_channel(newPage.ch.get_channel())
            self.window.status.set_current_subset(newPage.ch)
        except AttributeError:
            pass

    def close_current_page(self, evt=None):
        ind = self.GetPageIndex(self.GetCurrentPage())
        self.DeletePage(ind)


class PlotNotebook(Notebook):
    def __init__(self, parent):
        Notebook.__init__(self, parent)
        self.window = self.GetTopLevelParent()

        # load the channel editor in sorted order
        sorted_channel_names = self.window.data.get_channels()
        sorted_channel_names.sort()
        for channel_name in sorted_channel_names:
            channel = self.window.data.channels[channel_name]
            self.add_channel_editor(channel)

        self.window.Bind(dts.ui.evt.EVT_CHANNEL_IMPORTED, self.on_channel_imported)

    def update_active_main(self, page):
        if page.__class__.__name__ is 'MainViewer':
            self.active_main = page

    def update_pages(self):
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.update()

    def get_current_page(self):
        return self.GetCurrentPage()

    def get_active_main(self):
        return self.active_main

    def add_channel_editor(self, channel=None):

        if channel is None:
            channel = self.window.status.get_current_channel()

        page = ChannelEditorPanel(self, channel)
        name = "Editor: " + channel.get_title()
        self.AddPage(page, name)
        page_idx = self.GetPageIndex(page)
        self.SetCloseButton(page_idx, False)
        return page

    def add_main(self, dataset=None):

        window = self.GetTopLevelParent()

        if dataset is None:
            dataset = window.status.current_channel.data

        from dts.ui.plot.main import MainViewer
        page = MainViewer(self, dataset)
        self.update_active_main(page)
        channel = dataset.get_channel()
        if channel.get_title() == dataset.get_title():
            name = "Viewer: "+dataset.get_title()
        else:
            name = "Viewer: {}, {}".format(channel.get_title(), dataset.get_title())

        self.AddPage(page, name)
        return page

    def add_map(self):
        from dts.ui.map.static import StaticMapBase
        panel = StaticMapBase(self)
        self.AddPage(panel, 'Static Map')
        self.map = panel
        return panel

    def add_gmap(self):
        from dts.ui.map.google import GoogleMapControl
        gmap = GoogleMapControl(self)
        window = self.GetTopLevelParent()
        channel_title = window.data.ch.get_title()
        self.AddPage(gmap, 'Google Maps: {}'.format(channel_title))
        self.gmap = gmap
        return gmap

    def add_stats_gmap(self):
        from dts.ui.map.google import StatsGoogleMapControl
        stats_gmap = StatsGoogleMapControl(self)
        self.AddPage(stats_gmap, 'Google Maps: Multi-channel statistics')
        self.stats_gmap = stats_gmap
        return stats_gmap

    def add_subset_editor(self, subset=None):
        if subset is None:
            title = "Add new subset"
        else:
            title = "Edit subset '{}'".format(subset.get_title())
        from dts.ui.panels.subset_editor import SubsetEditor
        log.debug("Starting subset editor.")
        page = SubsetEditor(self, subset)
        self.AddPage(page, title, True)

        return page

    def add_data_explorer(self):
        from dts.ui.panels.ds_explorer import DataExplore
        page = DataExplore(self)
        self.AddPage(page, "Dataset Explorer")
        return page

    def add_import_geodata(self):
        from dts.ui.panels.import_geodata import import_geodata
        import_geodata(self)

    def add_subset_manager(self):
        from dts.ui.panels.subset_manager import SubsetManager
        log.debug("Starting subset manager.")
        page = SubsetManager(self)
        window = self.GetTopLevelParent()
        channel_title = window.data.ch.get_title()
        self.AddPage(page, "Subset Manager: {}".format(channel_title))
        return page

    def add_trim_raw(self, channel=None):
        from dts.ui.panels.trim_raw import TrimRaw
        page = TrimRaw(self)
        self.AddPage(page, "Trim Raw Data")
        return page

    def add_interval_offset(self):
        from dts.ui.panels.set_interval_offset import OffsetPanel
        page = OffsetPanel(self)
        self.AddPage(page, "Set interval and offset")

    def on_channel_imported(self, event):

        try:
            stats_gmap_idx = self.GetPageIndex(self.stats_gmap)
            self.DeletePage(stats_gmap_idx)
            delattr(self, 'stats_gmap')
        except AttributeError:
            pass

        event.Skip()
