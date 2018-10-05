import wx
import dts
from dts.ui.panels import NotebookChildPanel as Panel
from dts.ui.plot import PlotPanel
from dts.ui.map import MapControlBase
import numpy as N
from dts.ui.map.static.image import MapImage
import logging as log
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
from dts.ui.colors import GRAY


class ImageReminderBar(Panel):
    def __init__(self, parent):
        Panel.__init__(self,parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        if wx.Platform == "__WXMSW__":
            self.SetBackgroundColour(self.Parent.GetBackgroundColour())

        text="Display a map of the study area."
        self.text = dts.ui.controls.Fieldset(self, "Import a map", text=text)
        sizer.Add(self.text, 1, wx.EXPAND|wx.GROW|wx.ALL,0)

        self.button = wx.Button(self, wx.ID_ANY, 'Open map file')

        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.LEFT, 10)
        self.SetSizer(sizer)


class StaticMapBase(Panel):
    def __init__(self, parent, filename=None):
        Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if wx.Platform == "__WXMSW__":
            self.SetBackgroundColour(wx.Colour(180,180,180))

        if filename is None:
            log.info("No image loaded.")
            self.top_bar = ImageReminderBar(self)
            sizer.Add(self.top_bar, 0, wx.ALL, 10)

            self.top_bar.Bind(wx.EVT_BUTTON, self._onSetImageRequested)
        else:
            log.info("Image with filename {0} is loaded.".format(filename))
            self.top_bar = None

        self.map = MapViewer(self,filename=None)
        sizer.Add(self.map, 1, wx.EXPAND|wx.GROW, 0)
        """try:
            self.map = MapViewer(self,filename=None)
            sizer.Add(self.map, 1, wx.EXPAND|wx.GROW, 0)
        except Exception, error:
            log.exception(error)
            self.Destroy()"""

        self.SetSizer(sizer)

        # wx.FutureCall(1, self.Layout)
        # This is necessary because the panel won't initialize if just call the function. Hackish, but what can you do?

    def _onSetImageRequested(self, event):
        from dts.ui.dialog.file_io import choose_file
        filename = choose_file('Choose a GDAL-compatible image file')

        self.map.load_image(filename)
        self.top_bar.Destroy()
        self.GetSizer().Layout()


class MapViewer(PlotPanel, MapControlBase):
    def __init__(self, parent, filename = None):
        PlotPanel.__init__(self, parent, id=wx.ID_ANY, dpi=None, toolbar=MapToolbar)
        self.window = self.GetTopLevelParent()
        self.setupData()

        self.offset = 0
        self.temp_extents = None
        self.space_series = None
        self.x_loc = None
        self.t_loc = None

        try:
            viewer = dts.ui.active_viewer
            self.temp_extents = viewer.get_temp_extents()
            self.space_series = viewer.get_space_series()
            self.x_loc = viewer.x_loc
            self.t_loc = viewer.t_loc
        except:
            self.x_loc = 0
            self.t_loc = 0
            self.temp_extents = None
            self.space_series = None

        self.ax = False
        self.I = False

        self.points = None

        if filename != None: self.load_image(filename)

        self.interpolate = False

        if self.ch.geodata.loaded:
            self.set_projection()
            self.plot_points()
            self.bindEvents()
            self.update_colors()

        self._SetSize()

    def bindEvents(self):
        self.window.Bind(dts.ui.evt.EVT_COLORMAP_CHANGED, self.update_colors)

        self.toolbar.Bind(wx.EVT_CHECKBOX, self._onCheck)

        self.window.Bind(dts.ui.evt.EVT_TOOLTIP_MOVED, self._onTooltipMoved)
        self.window.Bind(dts.ui.evt.EVT_OFFSET_SET, self._onOffsetSet)

        self.canvas.mpl_connect('pick_event', self._onPick)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self._onKey)
        self.canvas.Bind(wx.EVT_KEY_UP, self._onKeyRelease)

    def _onOffsetSet(self, event):
        self.plot_points(event.interpolated)
        self.update_colors()
        log.info("Interval and offset updated in {0}".format(self.__class__.__name__))
        event.Skip()

    def _onTooltipMoved(self, event):
        if not self:
            event.Skip()
            return

        if self.points is None:
            event.Skip()
            return

        x_loc = event.x_loc
        t_loc = event.t_loc

        if event.source != self:
            if t_loc != self.t_loc:
                self.update_colors(event)

        self.__draw_selected_point(event.x_loc)
        if event.x_loc is not None:
            self.x_loc = x_loc
        if event.t_loc is not None:
            self.t_loc = t_loc
        event.Skip()
        log.debug("Tooltip moved in {0}".format(self.__class__.__name__))

    def __draw_selected_point(self, x_loc):
        point = self.points[x_loc]
        if point is not None:
            data = point.get_xydata()[0]
            self.selected.set_data(data[0], data[1])
            self.selected.set_visible(True)
            self.canvas.draw()

    def _onKey(self, evt):
        '''Moves the tooltip if the arrow keys are pressed'''
        code = evt.KeyCode
        if code == wx.WXK_LEFT: self.x_loc -= 1
        if code == wx.WXK_RIGHT:self.x_loc += 1
        self.__draw_selected_point(self.x_loc)

    def _onKeyRelease(self, evt):
        '''only redraw graph panel key is released (to prevent lag)'''
        self.__fireMoveTooltipEvent()

    def _onPick(self, event):
        log.info("Point picked.")
        #if event.artist!=self.line: return True
        self.x_loc = event.artist.index
        self.__fireMoveTooltipEvent()

    def __fireMoveTooltipEvent(self):
        log.debug("x_loc: {0}".format(int(self.x_loc)))
        from dts.ui.evt import TooltipMovedEvent
        event = TooltipMovedEvent(-1, x_loc=self.x_loc, t_loc=None, dataset=self.ch.data, source=self)
        wx.PostEvent(self, event)

    def _onCheck(self, evt):
        if self.toolbar.interpolate.GetId() == evt.GetId():
            self.interpolate = evt.Checked()
            if self.interpolate:
                self.plot_interpolated()
            else:
                self.plot_points()

    def do_layout(self):
        pass

    def load_image(self, filename=None):
        if filename is not None:
            self.I = MapImage(filename)
            self.set_projection()
            self.plot_points()
            return True
        else:
            return False

    def load_spatial(self, utm_zone=None):
        from dts.ui.map.static.spatial import Spatial
        self.I = Spatial()

    def update_offset(self):
        if self.interpolate:
            self.plot_interpolated()
        else:
            self.plot_points()

    def set_projection(self):
        if self.ax: self.figure.delaxes(self.ax)
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9,0.9])
        self.ax.set_axis_off()

        if self.I:
            if self.I.image is not None:
                self.im = self.ax.imshow(self.I.image)

        else:
            self.im = None
            self.ax.set_aspect('equal')

    def map(self, lon, lat):
        if self.I:
            return self.I.get_pixel(lon, lat)
        else:
            return lon, lat

    def plot_points(self, interp_lengths=None):
        if interp_lengths is None:
            interp_lengths = self.ch.geodata.interp

        # Handles cases where lengths are not interpolated.
        # BUG #
        if interp_lengths is None or False:
            log.info("No interpolated data found.")
            return

        if self.points is not None:
            for i in self.points:
                if i is not None: i.remove()
        if 'selected' in self.__dict__:
            self.selected.remove()
        self.points = []
        self.locations = []
        for i, interp in enumerate(interp_lengths):
            if interp[1] == -200:
                plt = None
            else:
                x, y = self.map(interp[1], interp[2])
                self.locations.append([x, y])
                plt, = self.ax.plot(x, y, 'ro', picker=5)
                plt.index = i
            self.points.append(plt)

        self.selected, = self.ax.plot(x, y, 'o', ms=12, alpha=0.4, color='yellow', visible=False)
        self.canvas.draw()

        self.locations = N.array(self.locations)

    def plot_interpolated(self, x_loc=None, interp_lengths=None):
        if interp_lengths is None:
            interp_lengths = self.ch.geodata.get_interpolated()

        cmap = graph.get_colormap()
        temps = graph.data[graph.t_loc, :]

        zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method='cubic')

        xs = []
        ys = []
        for i in self.geodata.interp:
            if i[1] == -200:
                x = None
                y = None
            else:
                x, y = self.map(i[1], i[2])

            xs.append(x)
            ys.append(y)

        self.points = self.ax.contourf(xs, ys, temps, 100, cmap=cmap)

        self.canvas.draw()

    def update_colors(self, event = None):
        if event is not None:
            if hasattr(event,"temp_extents"):
                self.temp_extents = event.temp_extents
            if hasattr(event, "space_series"):
                self.space_series = event.space_series
            if hasattr(event, "dataset"):
                self.offset = event.dataset.get_xmin()
        if self.space_series is not None and self.temp_extents is not None:
            cmap = None
            if hasattr(event, "cmap"):
                cmap = event.cmap
            colors = self.get_marker_colors(self.temp_extents, self.space_series, cmap)
            if self.interpolate:
                pass
            else:
                for i, point in enumerate(self.points):
                    if point is not None:
                        idx = point.index - self.offset
                        if idx < 0:
                            idx = None
                        try:
                            color = colors[idx]
                        except:
                            color = GRAY
                        point.set_markerfacecolor(color)
        self.canvas.draw()
        if event is not None:
            event.Skip()


class MapToolbar(Toolbar):
    def __init__(self, parent):
        Toolbar.__init__(self, parent)

        SUBPLOTS_BTN = 6
        self.DeleteToolByPos(SUBPLOTS_BTN)

        #self.interpolate = self.add_chkbox('Interpolate')

    def add_chkbox(self, label):
        ctrl = wx.CheckBox(self, -1, label)
        self.AddControl(ctrl)
        return ctrl
