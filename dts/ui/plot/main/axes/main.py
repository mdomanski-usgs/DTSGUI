from dateutil.tz import tzlocal

import dts
from dts.ui.plot.main.axes import AxesBase
import matplotlib.dates as dates
import matplotlib
import logging as log
import wx


class MainPlot(AxesBase):

    """The main plot axes, used both for the Main Viewer and for other classes (such as the more general PlotImage
    class) throughout the GUI."""
    name = 'MainPlot'

    def __init__(self, *args, **kwargs):
        AxesBase.__init__(self, *args, **kwargs)
        self.window = self.figure.window

        self.image = self.imshow(self.figure.parent.array, aspect='auto', cmap=self.get_colormap(),
                                 clim=self.get_clim(), interpolation="nearest")
        self.autoscale(False)

        self.xaxis.set_tick_params(labelbottom=False, labeltop=True)
        self.set_xlabel('Distance along cable (m)')
        self.xaxis.set_label_position('top')

        self.set_ylabel('Time')

        self._set_time_ticks()
        self._set_distance_ticks()

    def get_colormap(self):
        return self.window.colors.get_colormap()

    def get_clim(self):
        return self.window.colors.get_temp_extents()

    def _onColormapChanged(self, event):
        try:
            self.image.set_cmap(event.cmap)
            self.canvas.draw()
        except wx.PyDeadObjectError:
            pass
        event.Skip()

    def _on_clim_changed(self, event):
        self.image.set_clim(event.temp_extents)
        self.canvas.draw()
        event.Skip()

    def _onOffsetSet(self, event):
        self._set_distance_ticks(event)
        log.info("Interval and offset updated in {0}".format(self.__class__.__name__))

    def _distance_ticks(self, interval=None, offset=None):
        data = self.figure.parent.data

        if interval is None: interval = data.get_interval()
        if offset is None: offset = data.get_offset()

        log.debug("Setting distance ticks: Interval: {0}, Offset: {1}".format(interval, offset))

        ls = range(data.get_array().shape[1])
        ls = ["{0:.2f}".format(i*interval+offset) for i in ls]
        return ls

    def _set_distance_ticks(self, event=None):
        locator = matplotlib.ticker.MaxNLocator(nbins = 8)
        self.xaxis.set_major_locator(locator)

        log.debug("Setting distance ticks.")

        interval = None
        offset = None
        if event is not None:
            if hasattr(event, 'interval'):
                interval =  event.interval
            if hasattr(event, 'offset'):
                offset =  event.offset

        formatter = matplotlib.ticker.IndexFormatter(self._distance_ticks(interval, offset))
        self.xaxis.set_major_formatter(formatter)

        if event is not None:
            self.canvas.draw()

    def _set_time_ticks(self, event=None):
        locator = matplotlib.ticker.MaxNLocator(
            nbins=8,
            prune="both"
            )
        self.yaxis.set_major_locator(locator)

        log.debug("Setting time ticks.")

        times = self.figure.parent.data.get_times_list()
        time_format = dts.ui.time_format.get_format()
        times = dates.epoch2num(times)
        formatter = dates.IndexDateFormatter(times, time_format, tz=tzlocal())
        self.yaxis.set_major_formatter(formatter)

        if event is not None:
            self.canvas.draw()

