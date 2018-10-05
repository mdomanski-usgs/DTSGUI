import os
from dts.ui.plot import PlotPanel
from dts.ui.plot.main.toolbar import MainPlotToolbar, DisplayOptionsToolbar
from dts.ui.plot.main.grid import MainGridSpec
import numpy as np
from axes import *
import wx
import dts.ui.evt as evt


class MainViewer(PlotPanel):
    c_flags = dict(minmax=False, std=False, mean=False)
    displayOptions = None
    grid = False  # Have to set this so that we don't try to resize a nonexistent grid!

    def __init__(self, parent, dataset, id=wx.ID_ANY, dpi=None, **kwargs):
        # if dataset is None:
        # dataset = self.GetTopLevelParent().status.current_channel
        self.data = dataset
        self.array = self.data.get_array()
        # self.dataset = dataset

        f = lambda x, a: x(self.array[:], axis=a)
        self.profiles = {
            'time': {
                'min': f(np.amin, 1),
                'max': f(np.amax, 1),
                'mean': f(np.mean, 1),
                'std': f(np.std, 1)
                },
            'space': {
                'min': f(np.amin, 0),
                'max': f(np.amax, 0),
                'mean': f(np.mean, 0),
                'std': f(np.std, 0)
                }
            }

        PlotPanel.__init__(self, parent, id=id, dpi=None, toolbar=MainPlotToolbar, **kwargs)
        self.displayOptions = DisplayOptionsToolbar(self)

        self.grid = MainGridSpec(self)
        self.window = self.GetTopLevelParent()

        self.update()

        self.canvas.mpl_connect('button_press_event', self._onclick)

        self.canvas.Bind(wx.EVT_KEY_DOWN, self._onKey)
        # for some reason this doesn't work in windows...(arrow keys seemingly cannot be bound to?)
        # EDIT: actually, arrow keys are bound, but this only works when ALT+arrow key is pressed. Odd...
        self.canvas.Bind(wx.EVT_KEY_UP, self._onKeyRelease)

        self.toolbar.Bind(wx.EVT_CHECKBOX, self._onCheck)
        self.displayOptions.Bind(wx.EVT_CHECKBOX, self._onSubplotsAdjust)

        self.window.Bind(evt.EVT_MAP_UPDATED, self.__fireMoveTooltipEvent)
        self.window.Bind(evt.EVT_DATE_FORMAT_SET, self.main._set_time_ticks)
        self.window.Bind(evt.EVT_TOOLTIP_MOVED, self._onTooltipMoveEvent)
        self.window.Bind(evt.EVT_COLORMAP_CHANGED, self.main._onColormapChanged)
        self.window.Bind(evt.EVT_COLORMAP_ADJUSTED, self._on_colormap_adjusted)
        self.window.Bind(evt.EVT_OFFSET_SET, self.main._onOffsetSet)

        temp_extents = self.window.colors.get_temp_extents()
        if temp_extents is None:
            temp_extents = self.data.get_temp_range()
            self.window.colors.set_temp_extents(self, temp_extents)
        else:
            self._set_temp_extents(*temp_extents)

        self._SetSize()

        self.displayOptions.cbar_extents.set_auto_clim()

        dts.ui.active_viewer = self

    def set_tooltip_position(self, x_loc, t_loc):
        """Directly sets the tooltip position and fires the event to update the GUI."""
        self.x_loc = x_loc
        self.t_loc = t_loc
        self.move_tooltip()

    def _onCheck(self, evt):
        for key, item in self.toolbar.params.items():
            if item.GetId() == evt.GetId():
                self.c_flags[key] = evt.Checked()
                for i in (self.c_ax.series[key], self.t_ax.series[key]):
                    i.set_visible(self.c_flags[key])
                if key is 'std':
                    for i in (self.c_ax, self.t_ax):
                        i.std_ax.set_visible(self.c_flags[key])
                        mpl.axes.Axes.set_visible(self.info, not self.c_flags[key])
                else:
                    [ax.relim() for ax in [self.t_ax, self.c_ax]]
                    self.t_ax.autoscale_view(tight=True, scalex=True, scaley=False)
                    self.c_ax.autoscale_view(tight=True, scalex=False, scaley=True)

                self.canvas.draw()
        evt.Skip()

    def _SetSize(self):
        if self.grid:
            self.grid.set_ratios()
        PlotPanel._SetSize(self)

    def _onSubplotsAdjust(self, evt):
        checkboxes = self.displayOptions.subplots
        for key, item in checkboxes.items():
            getattr(self, key).set_visible(item.GetValue())
        val = checkboxes["c_ax"].GetValue() * checkboxes["t_ax"].GetValue()
        self.info.set_visible(val)

    def _on_colormap_adjusted(self, event):
        """

        :param event:
        :return:
        """
        if event.source == self:
            event.Skip()
            return

        min, max = event.temp_extents

        try:
            self._set_temp_extents(min, max)
            self.displayOptions.cbar_extents.set_min(min)
            self.displayOptions.cbar_extents.set_max(max)
        except wx.PyDeadObjectError:
            pass

        event.Skip()

    def _onKey(self, evt):
        """Moves the tooltip if the arrow keys are pressed."""
        code = evt.KeyCode
        if code == wx.WXK_DOWN:
            self.t_loc += 1
        if code == wx.WXK_UP:
            self.t_loc -= 1
        if code == wx.WXK_LEFT:
            self.x_loc -= 1
        if code == wx.WXK_RIGHT:
            self.x_loc += 1
        self.move_tooltip()

    def _onKeyRelease(self, evt):
        """only redraw map panel when key is released (to prevent lag)"""
        self.__fireMoveTooltipEvent()

    def _onTooltipMoveEvent(self, event):
        if event.source is self:
            t_loc = event.t_loc
            x_loc = event.x_loc
            trng = self.data.get_trange()
            xrng = self.data.get_xrange()

            if t_loc is not None and trng[0] <= t_loc <= trng[1]:
                self.t_loc = t_loc
            if x_loc is not None and xrng[0] <= x_loc <= xrng[1]:
                self.x_loc = x_loc

            if self.data.__class__.__name__ == "Subset":
                bounds = self.data.get_bounds()
                self.t_loc -= bounds["t_min"]
                self.x_loc -= bounds["x_min"]

            try:
                log.debug("Moving tooltip to {},{} in {} showing {}".format(self.x_loc, self.t_loc,
                                                                            self.__class__.__name__,
                                                                            self.data.array.name))
                self.move_tooltip()
            except IndexError:
                log.debug("Clearing tooltip in {} showing {}".format(self.__class__.__name__, self.data.array.name))
                self.clear_tooltip()

        event.Skip()

    def _onclick(self, event):
        if event.inaxes is self.main:
            self.x_loc = int(event.xdata)
            self.t_loc = int(event.ydata)
            log.debug("Click in {} at {}, {}".format("main axes", self.x_loc, self.t_loc))
        elif event.inaxes is self.t_ax.std_ax:
            self.t_loc = int(event.ydata)
            log.debug("Click in {} at {}".format("time axes", self.t_loc))
        elif event.inaxes is self.c_ax.std_ax:
            self.x_loc = int(event.xdata)
            log.debug("Click in {} at {}".format("cable axes", self.x_loc))

        self.__fireMoveTooltipEvent()

    def _set_temp_extents(self, min=None, max=None):
        """

        :param min:
        :param max:
        :return:
        """

        if min is None or max is None:
            mn, mx = self.data.get_temp_range()
        if min is None:
            min = mn
        if max is None:
            max = mx

        log.debug("Adjusting temp_extents in {} showing {} to {}, {}".format(self.__class__.__name__,
                                                                             self.data.get_title(), min, max))

        self.main.image.set_clim(min, max)
        self.canvas.draw()

    def get_space_series(self):

        return self.array[self.t_loc, :]

    def __fireMoveTooltipEvent(self, event=None):
        from dts.ui.evt import TooltipMovedEvent
        log.debug("Firing MoveTooltipMovedEvent for {} showing {}".format(self.__class__.__name__,
                                                                          self.data.array.name))

        t_loc = int(self.t_loc)
        x_loc = int(self.x_loc)

        if self.data.__class__.__name__ == "Subset":
            bounds = self.data.get_bounds()
            t_loc += bounds["t_min"]
            x_loc += bounds["x_min"]

        log.debug("x_loc: {0}, t_loc: {1}".format(x_loc, t_loc))

        event = TooltipMovedEvent(-1,
                                  x_loc=x_loc,
                                  t_loc=t_loc,
                                  dataset=self.data,
                                  temp_extents=self.get_temp_extents(),
                                  space_series=self.get_space_series(),
                                  time_series=self.array[:, self.x_loc],
                                  source=self
                                  )
        wx.PostEvent(self, event)

    def update(self):
        self.x_loc = 0
        self.t_loc = 0
        self.cable_plot(True)
        self.time_plot(True)
        self.main_plot()
        self.colorbar(True)
        self.info_panel()
        self.move_tooltip()

    def move_tooltip(self):

        temps = self.array[:, self.x_loc]
        self.t_ax.series['temp'].set_xdata(temps)

        cable = self.array[self.t_loc, :]
        self.c_ax.series['temp'].set_ydata(cable)

        self.window.status.x_loc = self.x_loc
        self.window.status.t_loc = self.t_loc

        color_options = self.window.colors.plot_overlay
        if 'tooltip' not in self.__dict__:
            self.tooltip, = self.main.plot(self.x_loc, self.t_loc, '+', markersize=20, markeredgewidth=2,
                                           **color_options)
            self.t_line = self.t_ax.axhline(self.t_loc, linewidth=2, **color_options)
            self.c_line = self.c_ax.axvline(self.x_loc, linewidth=2, **color_options)
        else:
            self.tooltip.set_data(self.x_loc, self.t_loc)
            self.t_line.set_ydata([self.t_loc, self.t_loc])
            self.c_line.set_xdata([self.x_loc, self.x_loc])

        self.tooltip.set_marker('+')
        self.t_line.set_linestyle('-')
        self.c_line.set_linestyle('-')

        self.info.update()
        self.canvas.draw()

    def get_colormap(self):
        return self.window.colors.get_colormap()

    def set_colormap(self):
        cmap = self.get_colormap()
        self.main.image.set_cmap()

    def main_plot(self, shared=True):
        if 'main' in self.__dict__:
            self.main.clear()
            self.main.autoscale(True)
        else:
            if shared:
                opts = dict(sharey=self.t_ax, sharex=self.c_ax)
            else:
                opts = dict()
            self.main = self.figure.add_subplot(self.grid[2], projection="MainPlot", **opts)

    def get_mainmap(self):
        return self.main.image.get_cmap()

    def get_temp_extents(self):
        return self.main.image.get_clim()

    def temp_extents_autoset(self):
        """Returns a boolean whether the temperature extents are set to defaults."""
        mn, mx = self.data.get_temp_range()
        gm, gx = self.get_temp_extents()
        if mn != gm:
            return False
        if mx != gx:
            return False
        return True

    def set_temp_extents(self, min=None, max=None):
        if min > max:
            raise ValueError("min must be greater than max")
        self._set_temp_extents(min, max)

        self.window.colors.set_temp_extents(self, (min, max))

    def colorbar(self, update=False):
        if 'cbar' in self.__dict__:
            self.cbar.clear()
        else:
            location = self.grid.new_subplotspec((0,0), rowspan=2)
            self.cbar = self.figure.add_subplot(location, projection='ColorBar')

    def time_plot(self, update=False):
        if 't_ax' in self.__dict__:
            self.t_ax.clear()
        else:
            self.t_ax = self.figure.add_subplot(self.grid[3], projection='TimePlot')
            mn, mx = self.data.get_temp_range()
            self.t_ax.set_xlim(mn, mx)

    def cable_plot(self, update=False):
        if 'c_ax' in self.__dict__:
            self.c_ax.clear()
        else:
            self.c_ax = self.figure.add_subplot(self.grid[6], projection='CablePlot')
            mn, mx = self.data.get_temp_range()
            self.c_ax.set_ylim(mn, mx)

    def info_panel(self):
        if 'info' not in self.__dict__:
            self.info = self.figure.add_subplot(self.grid[7], projection='InfoPanel')

    def clear_tooltip(self):
        self.tooltip.set_marker('')
        self.t_line.set_linestyle('')
        self.c_line.set_linestyle('')
        self.canvas.draw()
