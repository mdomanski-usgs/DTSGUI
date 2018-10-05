import os

import wx
import dts

import matplotlib.style
import matplotlib as M
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx

from dts.ui.panels import Panel

import logging as log

M.style.use('classic')


class PlotFigure(M.figure.Figure):
    def __init__(self, parent, *args, **kwargs):
        M.figure.Figure.__init__(self, *args, **kwargs)
        self.parent = parent
        self.window = parent.GetTopLevelParent()


class PlotPanel(Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a
    flag, and the actual resizing of the figure is triggered by an Idle event."""
    def __init__(self, parent, id=-1, dpi=300, toolbar=None, **kwargs ):
        if 'style' not in kwargs.keys(): kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        Panel.__init__(self, parent, id=id, **kwargs)

        self.figure = PlotFigure(self, dpi=dpi, facecolor='#dddddd')
        self.canvas = Canvas(self, -1, self.figure)

        self._resizeflag = False

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        if toolbar is None:
            toolbar = NavigationToolbar2Wx
        self.toolbar = toolbar(self.canvas)
        self.toolbar.Realize()
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

        self.SetSizer(self.sizer)

        # Breaks toolbar position for some reason??
        self.Parent.Bind(wx.EVT_IDLE, self._onIdle)
        self.Parent.Bind(wx.EVT_SIZE, self._onSize)
        self._SetSize()

    def _onSize(self, evt):
        self._resizeflag = True
        evt.Skip()

    def _onIdle(self, evt):
        if self:
            if self._resizeflag:
                self._resizeflag = False
                self._SetSize()
                evt.Skip()

    def _SetSize(self):
        pixels = self.GetSizeTuple()
        self.SetSize( pixels )
        self.canvas.draw()

    def draw(self):
        pass  # to be overridden by subclasses

    def save_image(self):
        """

        :return:
        """
        valid_dpi = False
        while not valid_dpi:
            with wx.TextEntryDialog(self, "Enter a DPI for the image:", caption="Image DPI") as \
                    text_entry_dlg:
                text_entry_dlg.CenterOnParent()
                text_entry_dlg.SetValue("100")
                if text_entry_dlg.ShowModal() == wx.ID_OK:
                    try:
                        image_dpi = int(text_entry_dlg.GetValue())
                        if image_dpi < 4:
                            raise ValueError
                        valid_dpi = True
                    except ValueError:
                        with wx.MessageDialog(self, "Invalid DPI entry. Enter a valid DPI.", caption="Invalid DPI",
                                              style=wx.OK | wx.CENTER | wx.ICON_ERROR) as msg_dlg:
                            msg_dlg.ShowModal()
                else:
                    return

        # modified from matplotlib.backends.backend_wxagg.NavigationToolbar2Wx.save_figure()
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = self.canvas.get_default_filename()
        dlg = wx.FileDialog(self, "Save to file", "", default_file,
                            filetypes,
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(filter_index)
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            filename = dlg.GetFilename()
            format = exts[dlg.GetFilterIndex()]
            basename, ext = os.path.splitext(filename)
            if ext.startswith('.'):
                ext = ext[1:]
            if ext in ('svg', 'pdf', 'ps', 'eps', 'png') and format != ext:
                format = ext

            self.canvas.print_figure(
                os.path.join(dirname, filename), format=format, dpi=image_dpi)


from matplotlib.patches import Rectangle
from dts.ui.plot.main.axes.main import MainPlot
from matplotlib.projections import register_projection
register_projection(MainPlot)


class PlotImage(PlotPanel):
    def __init__(self, parent, data=None):
        PlotPanel.__init__(self, parent, id=wx.ID_ANY, dpi=None)

        self.window = self.GetTopLevelParent()
        self.data = data
        if self.data is None:
            self.data = self.window.status.get_current_channel().data
        self.array = self.data.get_array()
        self.hdf = self.data.__hdf__
        # self.dataset = self.window.status.get_current_channel()
        self.dataset = self.data.get_channel()

        self._draw()
        self.window.Bind(dts.ui.evt.EVT_DATE_FORMAT_SET, self.ax._set_time_ticks)
        self.window.Bind(dts.ui.evt.EVT_COLORMAP_CHANGED, self.ax._onColormapChanged)
        self.window.Bind(dts.ui.evt.EVT_OFFSET_SET, self.ax._onOffsetSet)
        self.window.Bind(dts.ui.evt.EVT_COLORMAP_ADJUSTED, self.ax._on_clim_changed)

    def _draw(self):

        self.ax = self.figure.add_axes([.08, .05, .9, .9], projection="MainPlot")

    def __unbind_events(self):
        self.window.Unbind(dts.ui.evt.EVT_DATE_FORMAT_SET, handler=self.ax._set_time_ticks)
        self.window.Unbind(dts.ui.evt.EVT_COLORMAP_CHANGED, handler=self.ax._onColormapChanged)
        self.window.Unbind(dts.ui.evt.EVT_OFFSET_SET, handler=self.ax._onOffsetSet)
        self.window.Unbind(dts.ui.evt.EVT_COLORMAP_ADJUSTED, handler=self.ax._on_clim_changed)

    def Destroy(self, *args, **kwargs):
        self.__unbind_events()
        log.debug("Destroying {}".format(self.__class__.__name__))
        super(PlotPanel, self).Destroy(*args, **kwargs)

    def plot_rectangle(self, extents):
        width = extents['space']['max'] - extents['space']['min']+1
        height = extents['time']['max'] - extents['time']['min']+1
        loc = (extents['space']['min']-0.5, extents['time']['min']-0.5)
        color_options = self.window.colors.plot_overlay
        return Rectangle(loc, width, height, facecolor='none', edgecolor=color_options['color'],
                         alpha=color_options['alpha'], linewidth=2)

    def plot_box(self, extents):
        rect = self.plot_rectangle(extents)
        if 'box' in self.__dict__:
            self.ax.patches.remove(self.box)
        self.box = self.ax.add_patch(rect)
        self.canvas.draw()

    def __reset_data(self, data):
        self.data = data
        self.draw()
