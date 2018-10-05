from datetime import datetime

import numpy as np

import wx
from wx.lib.scrolledpanel import ScrolledPanel

import dts
from dts.ui.dialog.offset import OffsetDialog


class ManagerPanel(wx.Panel):
    def __init__(self, parent, label, buttons=None):
        wx.Panel.__init__(self, parent)
        self.nb = dts.ui.tabset
        self.boxSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, label), wx.VERTICAL)
        self.SetSizer(self.boxSizer)

        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseMove)

        self.buttons = {}

        if buttons is not None:
            self.create_buttons(buttons)

        self.Parent.sizer.Add(self, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)

    def create_buttons(self, buttons):
        for item in buttons:
            self.add_button(**item)

    def onMouseMove(self, evt):
        """Allows parent panel to scroll"""
        parent = self.GetParent()
        evt.SetId(parent.GetId())
        evt.SetEventObject(parent)
        parent.GetEventHandler().ProcessEvent(evt)

    def add_button(self, name, title, description=None, callback=None):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_ANY, title, size=(200, -1))
        sizer.Add(btn, 0)
        if callback is not None:
            self.Bind(wx.EVT_BUTTON, callback, id=btn.GetId())
        if description is not None:
            t = wx.StaticText(self, label=description, size=(200, -1))
            sizer.Add(t, 2, wx.EXPAND | wx.GROW | wx.LEFT, 10)
        self.boxSizer.Add(sizer, 0, wx.EXPAND | wx.GROW | wx.TOP | wx.BOTTOM, 5)
        self.buttons[name] = btn
        return btn


class ChannelPanel(ManagerPanel):
    def __init__(self, parent):
        ManagerPanel.__init__(self, parent, "Channel")

        buttons = [{
                "name": "view_data",
                "title": "View Channel Data",
                "description": "View the data for this channel.",
                "callback": self.__doChannelViewer
            },
            {
                "name": "manage_subsets",
                "title": "Manage Subsets",
                "description": "View and manage subsets of the data.",
                "callback": self.__doSubsetManager
            },
            {
                "name": "set_offset",
                "title": "Set Interval and Offset",
                "description": "Set interval and offset of dataset relative to cable marks.",
                "callback": self.__doSetOffset
            },
            {
                "name": "trim_raw",
                "title": "Trim Raw Data",
                "description": "Trim raw dataset to smaller extent.",
                "callback": self.__doTrimRaw
            }
        ]
        self.create_buttons(buttons)

    def __doChannelViewer(self, event):
        self.nb.add_main(dataset=self.GetParent().ch.data)

    def __doSubsetManager(self, event):
        self.nb.add_subset_manager()

    def __doRawViewer(self, event):
        dataset = self.window.status.current_channel.data_raw
        self.nb.add_main(dataset)

    def __doTrimRaw(self, event):
        self.nb.add_trim_raw()

    def __doSetOffset(self, event):

        old_interval = self.Parent.ch.get_interval()
        old_offset = self.Parent.ch.get_offset()

        with OffsetDialog(self, wx.ID_ANY, offset=old_offset, interval=old_interval) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                new_interval = dlg.get_interval()
                new_offset = dlg.get_offset()
                self.Parent.ch.set_interval_offset(new_interval, new_offset)
                self.post_set_event()

    def post_set_event(self):
        interval = self.Parent.ch.get_interval()
        offset = self.Parent.ch.get_offset()
        interp_lengths = self.Parent.ch.geodata.interpolate(interval, offset)
        event = dts.ui.evt.OffsetSetEvent(-1,
                                          offset=offset,
                                          interval=interval,
                                          final=True,
                                          interpolated=interp_lengths
                                          )
        wx.PostEvent(self, event)


class SpatialPanel(ManagerPanel):
    def __init__(self, parent):
        ManagerPanel.__init__(self, parent, "Spatial")

        buttons = [
            {
                "name": "map",
                "title": "Static Map Viewer",
                "description": "Show geospatial data on a static map.",
                "callback": self.__doMap
            },
            {
                "name": "gmap",
                "title": "Google Maps Viewer",
                "description": "Show geospatial data on a Google Map.",
                "callback": self.__doGmap
            },
            {
                "name": "import_geodata",
                "title": "Import Geospatial Data",
                "description": "Import geospatial data from delimited text file.",
                "callback": self.__doImportGeospatial
            }
        ]
        self.create_buttons(buttons)

        self.window = self.GetTopLevelParent()

        parent = self.GetParent()
        if not parent.ch.geodata.loaded:
            self.buttons["gmap"].Enable(False)
            self.buttons["map"].Enable(False)

        self.window.Bind(dts.ui.evt.EVT_GEODATA_IMPORTED, self.on_geodata_imported)

    def on_geodata_imported(self, event):
        parent = self.GetParent()
        if event.channel == parent.ch:
            self.buttons["gmap"].Enable(True)
            self.buttons["map"].Enable(True)
        event.Skip()

    def __doMap(self, event):
        self.nb.add_map()

    def __doGmap(self, event):
        self.nb.add_gmap()

    def __doImportGeospatial(self, event):
        self.nb.add_import_geodata()


class ExportPanel(ManagerPanel):

    def __init__(self, parent):
        ManagerPanel.__init__(self, parent, "Export")

        window = self.GetTopLevelParent()

        buttons = [
            {
                "name": "csv",
                "title": "Subset as CSV",
                "description": "Save subset data as a CSV file.",
                "callback": self.save_data_as_csv
            },
            {
                "name": "csvstats",
                "title": "Subset stats as CSV",
                "description": "Save the statistics of the subset data as a CSV file.",
                "callback": self.save_data_stats_as_csv
            }
        ]

        self.create_buttons(buttons)

    def save_data_as_csv(self, event):

        window = self.GetTopLevelParent()
        parent = self.GetParent()
        window.save_active_data_as_csv(parent.ch)

    def save_data_stats_as_csv(self, event):

        window = self.GetTopLevelParent()
        parent = self.GetParent()
        window.save_active_data_stats(parent.ch)


class ChannelEditorPanel(ScrolledPanel):
    def __init__(self, parent, channel=None):
        ScrolledPanel.__init__(self, parent)
        self.window = self.GetTopLevelParent()
        self.nb = dts.ui.tabset

        if channel is None:
            self.ch = self.window.data.get_current_channel()
        else:
            self.ch = channel

        data = self.ch.get_array()[:]

        data_is_nan = np.isnan(data)

        if np.any(data_is_nan):

            nan_locations = np.where(data_is_nan)

            nan_location_output = ["NaN values encountered in {}\n".format(self.ch.get_title()),
                                   "Time                           Distance"]

            for time_index, dist_index in zip(*nan_locations):
                time = datetime.fromtimestamp(self.ch.get_time(time_index))
                dist = self.ch.get_dist(dist_index)
                nan_location_output.append("{}  {}".format(time, dist))

            msg = "\n".join(nan_location_output)
            with wx.MessageDialog(self, msg, "NaN values encountered", style=wx.OK | wx.CENTER) as msg_dlg:
                msg_dlg.ShowModal()

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.panels = {'channel': ChannelPanel(self), 'spatial': SpatialPanel(self), 'export': ExportPanel(self)}

        self.SetSizer(self.sizer)

        self.SetupScrolling()
