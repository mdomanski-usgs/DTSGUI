import matplotlib.pyplot as pyplot
import wx
import evt
import logging as log
import time_format

active_viewer = None
tabset = None


class ButtonFont(wx.Font):
    def __init__(self):
        fsize = 10
        if wx.Platform == '__WXMSW__':
            fsize = 8
        wx.Font.__init__(self, fsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)


class ColorManager(object):
    def __init__(self, parent):
        self.default_cmap = pyplot.get_cmap("jet")
        self.current_cmap = self.default_cmap
        self.temp_extents = None
        self.window = parent

        self.plot_overlay = dict(color="#cccccc", alpha=0.8)

        self.window.Bind(evt.EVT_COLORMAP_CHANGED, self.on_colormap_changed)

    def on_colormap_changed(self, event):
        self.set_colormap(event.cmap)
        event.Skip()
        log.info("Colormap changed to "+event.cmap.name)

    def set_colormap(self, cmap=None):
        """Sets the main colormap for the application. Takes a valid matplotlib colormap name or a colormap object."""
        if cmap is None:
            self.current_cmap = self.default_cmap
        else:
            self.current_cmap = cmap

    def get_colormap(self):
        """Gets the colormap currently in use for the application."""
        return self.current_cmap

    def get_colormap_list(self, all=False):
        """Here is a list of all the possible colormaps."""
        pass

    def set_temp_extents(self, source, temp_extents):
        """Set colormap limits"""
        assert isinstance(temp_extents, tuple)
        assert temp_extents[1] >= temp_extents[0]
        self.temp_extents = temp_extents

        log.debug("Firing color map adjusted event with {}, {}".format(*temp_extents))
        new_event = evt.ColormapAdjustedEvent(-1, source=source, temp_extents=temp_extents)
        wx.PostEvent(self.window, new_event)

    def get_temp_extents(self):
        """Returns current temperature extents"""
        return self.temp_extents


class WindowStateManager(object):
    def __init__(self, window):
        self.window = window
        self.dataset = window.data
        self.current_channel = None
        self.set_current_channel(self.dataset.ch)
        try:
            # initially set the values to the first channel and the first subset
            self.set_current_subset(self.dataset.ch.subsets.items()[0][1])
        except IndexError:
            log.error("No subsets found")
            self.current_subset = None

        log.info("Data initialization completed")

        self.window.Bind(evt.EVT_SUBSET_EDITED, self.on_subset_edited)

        self.map_control = None
        self.gmap_control = None

    def on_subset_edited(self, event):
        self.set_current_subset(event.subset)
        newevent = evt.SubsetSelectedEvent(wx.ID_ANY, new=event.new, subset=event.subset)
        wx.PostEvent(self.window, newevent)

    def get_current_channel(self):
        return self.current_channel

    def set_current_channel(self, channel):
        self.current_channel = channel
        self.window.data.set_working_channel(channel.get_title())
        event = evt.ChannelChangedEvent(wx.ID_ANY, new_channel=channel)
        wx.PostEvent(self.window, event)
        log.debug("Current channel set to {}".format(channel.get_title()))

    def get_current_subset(self):
        return self.current_subset

    def set_current_subset(self, subset):
        self.current_subset = subset
        log.debug("Current subset set to {}".format(subset.get_title()))

    def get_current_plot(self):
        pass

    def set_current_plot(self):
        pass
