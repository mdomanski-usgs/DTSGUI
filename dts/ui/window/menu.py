import abc

import wx
import dts
import logging as log


class Menu(wx.Menu):
    def __init__(self, parent, name, id=wx.ID_ANY):
        self.parent = parent
        self.window = parent.window
        wx.Menu.__init__(self)
        self.create()
        if parent.__class__.__name__ == "MenuBar":
            parent.Append(self, name)
        elif "Menu" in parent.__class__.__name__:
            self.id = id
            parent.AppendMenu(id, name, self)

    @abc.abstractmethod
    def create(self):
        """Creates the menu. Abstract function designed to be subclassed for each particular menu."""
        pass

    def add(self, text, hint="", handler=None, id=wx.ID_ANY):
        """Shorthand function to append and bind a menu item"""
        a = self.Append(id, text, hint)
        self.Bind(wx.EVT_MENU, handler, id=a.GetId())
        return a


class FileMenu(Menu):

    def create(self):

        self.add("Import data", "Adds new channel data", self.on_import_data)

        self.AppendSeparator()

        save_image_menu_item = self.add("Save image", "Save an image of the current panel", self.window.on_save_image)
        save_image_menu_item.Enable(False)

        self.AppendSeparator()

        self.add("&Save", "Save your data.", self.window.save_data, id=wx.ID_SAVE)

        if wx.Platform == '__WXMSW__':
            self.add("&Exit", "Quit DTS-GUI.", self.window.on_close, id=wx.ID_EXIT)

    def on_import_data(self, event):
        try:
            old_channels = set(self.window.data.get_channels())
            dts.Initialize(self.window.data)
            new_channels = set(self.window.data.get_channels())
            added_channel_name = new_channels.difference(old_channels).pop()
            # a = self.view_data.add(added_channel_name, handler=self.view_data.on_view_channel)
            # self.view_data.channel_menu_items.append(a)

            added_channel = self.window.data.channels[added_channel_name]
            dts.ui.tabset.add_channel_editor(added_channel)

            event = dts.ui.evt.ChannelImportedEvent(-1, channel_name=added_channel_name)
            wx.PostEvent(self.window, event)

        except ValueError:
            return


class ViewChannelMenu(Menu):

    def create(self):

        self.channel_menu_items = []
        for channel in self.window.data.get_channels():
            a = self.add(channel, handler=self.on_view_channel)
            self.channel_menu_items.append(a)

        self.window.Bind(dts.ui.evt.EVT_CHANNEL_IMPORTED, self.on_channel_imported)

    def on_view_channel(self, event):

        evt_id = event.GetId()

        for item in self.channel_menu_items:
            if evt_id == item.GetId():
                channel_name = item.GetLabel()
                channel_data = self.window.data.channels[channel_name].data
                dts.ui.tabset.add_main(dataset=channel_data)
                break

    def on_channel_imported(self, event):

        added_channel_name = event.channel_name
        print(event.channel_name)
        a = self.add(added_channel_name, handler=self.on_view_channel)
        self.channel_menu_items.append(a)


class RawDataMenu(Menu):
    def create(self):
        self.add("Trim", "Set boundaries of dataset for analysis.", self.on_trim)
        self.add("Revert", "Abandons all data for the dataset.", self.on_revert)

    def on_trim(self, event):
        dts.ui.tabset.add_trim_raw()

    def on_revert(self, event):
        dialog = wx.MessageDialog(self.window,
                                  'All trimming, optimization operations, and subsets will be lost.',
                                  'Are you sure you want to revert to raw data?',
                                  wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
                                  )
        if dialog.ShowModal() == wx.ID_YES:
            self.window.status.current_channel.revert_to_raw()
        dialog.Destroy()
        # dts.ui.tabset.update_pages()


class ViewMenu(Menu):
    def create(self):

        self.stats_google = self.add("Stats geospatial view", "View statistics of all data in Google Maps",
                                     self.on_view_stats_google_maps)

        if not self.all_geodata_loaded():
            self.stats_google.Enable(False)

        self.window.Bind(dts.ui.evt.EVT_GEODATA_IMPORTED, self.on_geodata_imported)
        self.window.Bind(dts.ui.evt.EVT_CHANNEL_IMPORTED, self.on_channel_imported)

    def all_geodata_loaded(self):

        for channel_name in self.window.data.get_channels():
            if not self.window.data.channels[channel_name].geodata.loaded:
                return False

        return True

    def on_channel_imported(self, event):
        if not self.window.data.channels[event.channel_name].geodata.loaded:
            self.stats_google.Enable(False)
        event.Skip()

    def on_geodata_imported(self, event):
        if self.all_geodata_loaded():
            self.stats_google.Enable(True)
        event.Skip()

    def on_view_stats_google_maps(self, event):

        self.window.tabs.add_stats_gmap()


class ViewSubsetMenu(Menu):
    def create(self):
        self.items = {}
        for channel_id in self.window.data.channels:
            for key, subset in self.window.data.channels[channel_id].subsets.items():
                self.add(subset)

        self.window.Bind(dts.ui.evt.EVT_SUBSET_EDITED, self.on_subset_edited)
        self.window.Bind(dts.ui.evt.EVT_SUBSET_DELETED, self.on_subset_deleted)

    def add(self, subset):
        callback = lambda evt, s=subset: self.on_view_subset(evt, s)
        channel = subset.get_channel()
        ctrl = Menu.add(self, channel.get_title() + ": " + subset.get_title(), "", callback)
        self.items[subset.get_key()] = ctrl

    def on_view_subset(self, event, subset=None):
        if subset is not None:
            dts.ui.tabset.add_main(dataset=subset)

    def on_subset_edited(self, event):
        if event.new:
            subset = event.subset
            self.add(subset)
            log.debug("Subset added to menu.")
        event.Skip()

    def on_subset_deleted(self, event):
        self.RemoveItem(self.items[event.key])
        log.debug("Subset deleted from menu")
        event.Skip()


class MapMenu(Menu):
    def create(self):
        self.add("Import geospatial data", "Allows the import of location data.", self.on_import_geodata)
        self.google = self.add("View Google Maps", "", self.on_view_google)
        self.static = self.add("View static map", "", self.on_view_static)

        if not self.window.data.ch.geodata.loaded:
            self.google.Enable(False)
            self.static.Enable(False)

        self.window.Bind(dts.ui.evt.EVT_GEODATA_IMPORTED, self.on_geodata_imported)

    def on_geodata_imported(self, event):
        self.google.Enable(True)
        self.static.Enable(True)
        event.Skip()

    def on_import_geodata(self, event):
        dts.ui.tabset.add_import_geodata()

    def on_view_google(self, event):
        dts.ui.tabset.add_gmap()

    def on_view_static(self, event):
        dts.ui.tabset.add_map()


class OptionsMenu(Menu):	
    def create(self):
        self.add("Change colormap", "Change to a new colormap.", self.window.on_set_colormap)
        self.timeformat = TimeFormatMenu(self, "Time format")
        if dts.DEBUG:
            self.AppendSeparator()

            self.debug = self.AppendCheckItem(-1, "Debug mode")

            self.debug.Check(True)
            self.log = LoggingMenu(self, "Logging level", id=12803)
            self.widget = self.add("Start widget inspector", "View wxPython widget inspector.", self.on_widget_inspector)
            self.Enable(self.log.id, dts.DEBUG)
            self.widget.Enable(dts.DEBUG)
            self.Bind(wx.EVT_MENU, self.on_debug, id=self.debug.GetId())

    def on_add_shell(self, event):
        dts.ui.tabset.add_shell()

    def on_debug(self, event):
        if event.Checked():
            dts.DEBUG = True
            log.info("Debug mode enabled.")
        if not event.Checked():
            dts.DEBUG = False
            log.info("Debug mode disabled.")
        self.Enable(self.log.id, dts.DEBUG)
        self.widget.Enable(dts.DEBUG)
        evt = dts.ui.evt.DebugModeChangedEvent(wx.ID_ANY, enabled=dts.DEBUG)
        wx.PostEvent(self, evt)

    def on_widget_inspector(self, event):
        self.window.GetApplication().ShowInspectionTool()


class LoggingMenu(Menu):

    def create(self):
        critical = self.AppendRadioItem(-1, 'Critical')
        error = self.AppendRadioItem(-1, 'Error')
        warning = self.AppendRadioItem(-1, 'Warning')
        info = self.AppendRadioItem(-1, 'Info')
        debug = self.AppendRadioItem(-1, 'Debug')

        self.Bind(wx.EVT_MENU, dts.logging.set_critical, id=critical.GetId())
        self.Bind(wx.EVT_MENU, dts.logging.set_error, id=error.GetId())
        self.Bind(wx.EVT_MENU, dts.logging.set_warning, id=warning.GetId())
        self.Bind(wx.EVT_MENU, dts.logging.set_info, id=info.GetId())
        self.Bind(wx.EVT_MENU, dts.logging.set_debug, id=debug.GetId())


class TimeFormatMenu(Menu):

    def create(self):
        month_day = self.AppendRadioItem(-1, 'Month/Day')
        julian = self.AppendRadioItem(-1, 'Julian Day')

        self.Bind(wx.EVT_MENU, self.set_julian, id=julian.GetId())
        self.Bind(wx.EVT_MENU, self.set_monthday, id=month_day.GetId())

    def set_julian(self, event):
        dts.ui.time_format.set_julian()
        event = dts.ui.evt.DateFormatSetEvent(wx.ID_ANY, formatter=dts.ui.time_format)
        wx.PostEvent(self.window, event)

    def set_monthday(self, event):
        dts.ui.time_format.set_monthday()
        event = dts.ui.evt.DateFormatSetEvent(wx.ID_ANY, formatter=dts.ui.time_format)
        wx.PostEvent(self.window, event)


class DebugMenu(Menu):
    def create(self):
        self.add("Start widget inspector", "View wxPython widget inspector.", self.on_widget_inspector)

    def on_widget_inspector(self, event):
        self.window.GetApplication().ShowInspectionTool()


class MenuBar(wx.MenuBar):
    def __init__(self, parent):
        self.parent = parent
        self.window = parent
        wx.MenuBar.__init__(self)
        self.parent.SetMenuBar(self)

        self.file = FileMenu(self, "File")
        self.subsets = ViewMenu(self, "View")
        self.options = OptionsMenu(self, "Options")

    def enable(self, menu, enabled=True):
        if enabled and self.debug is None:
            self.Append(menu, menu.GetTitle())
        else:
            self.RemoveItem(menu)
