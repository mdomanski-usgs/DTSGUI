import os

import numpy as np

import wx
import dts
import dts.ui.evt as evt
from dts.ui.controls.web import CPL_WebControl
from dts.ui.map import MapControlBase
import logging as log
import json
from dts.ui.colors import GRAY


class GoogleMapControl(CPL_WebControl, MapControlBase):
    def __init__(self, parent, **kwargs):

        CPL_WebControl.__init__(self, parent)

        self.offset = 0
        self.temp_extents = None
        self.x_loc = None
        self.t_loc = None
        self._space_series_values = None
        self.space_series = self._init_space_series()
        self._last_tooltip_move_event = None
        try:
            viewer = dts.ui.active_viewer
            self.temp_extents = viewer.get_temp_extents()
            self.x_loc = viewer.x_loc
            self.t_loc = viewer.t_loc
        except:
            pass

        log.info("Initializing {}".format(self.__class__.__name__))

        self.setupData()

        self.set_up_display()

        self.bindEvents()
        wx.FutureCall(1000, self.update_colors)

    def _init_space_series(self):
        self._space_series_values = 'inst'
        try:
            return dts.ui.active_viewer.get_space_series()
        except AttributeError:
            window = self.GetTopLevelParent()
            current_subset = window.status.get_current_subset()
            array = current_subset.get_array()
            return array[0, :]

    def Destroy(self, *args, **kwargs):
        log.debug("Destroying {}".format(self.__class__.__name__))
        self.unbind_events()
        super(GoogleMapControl, self).Destroy(*args, **kwargs)

    def set_up_display(self):

        from html import html
        self.LoadFileString(html, self._createMarkersJSON())

        sizer = self.GetSizer()

        current_channel_title = self.ch.get_title()
        self.current_channel_static_text = wx.StaticText(self,
                                                         label="Showing {}".format(current_channel_title))
        sizer.Add(self.current_channel_static_text)

        radio_box_choices = ['Inst.', 'Max', 'Min', 'Mean', 'Std']
        self.radio_box = wx.RadioBox(parent=self, style=wx.RA_SPECIFY_COLS, majorDimension=5,
                                     choices=radio_box_choices, label='Series Values')

        sizer.Add(self.radio_box, 0.1, wx.EXPAND, 0)

    def bindEvents(self):
        window = self.GetTopLevelParent()

        self.Bind(wx.EVT_KEY_DOWN, self._onKey)
        self.Bind(wx.EVT_KEY_UP, self._onKeyRelease)

        self.radio_box.Bind(wx.EVT_RADIOBOX, self._on_radio_box)

        window.Bind(evt.EVT_COLORMAP_CHANGED, self.update_colors)
        window.Bind(evt.EVT_COLORMAP_ADJUSTED, self.update_colors)
        window.Bind(evt.EVT_OFFSET_SET, self._onOffsetSet)
        window.Bind(evt.EVT_TOOLTIP_MOVED, self._onTooltipMoved)
        window.Bind(evt.EVT_TOOLTIP_MOVED, self.update_current_subset)

    def unbind_events(self):

        window = self.GetTopLevelParent()

        window.Unbind(evt.EVT_COLORMAP_CHANGED, handler=self.update_colors)
        window.Unbind(evt.EVT_COLORMAP_ADJUSTED, handler=self.update_colors)
        window.Unbind(evt.EVT_OFFSET_SET, handler=self._onOffsetSet)
        window.Unbind(evt.EVT_TOOLTIP_MOVED, handler=self._onTooltipMoved)
        window.Unbind(evt.EVT_TOOLTIP_MOVED, handler=self.update_current_subset)

    def on_move_tooltip(self, event):
        event.Skip()

    def _setCenterScript(self, center=None, update=None):
        if center is None:
            center = self.geodata.get_center()
        return "var center = new google.maps.LatLng({0}, {1}); window.map.setCenter(center);".format(center[0],
                                                                                                     center[1])

    def _onTooltipMoved(self, event):
        self._last_tooltip_move_event = event
        if not self:
            event.Skip()
            return

        if event.dataset.get_channel() is not self.ch:
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
        log.debug("Tooltip moved in {} showing {}".format(self.__class__.__name__, self.ch.get_title()))

    def __draw_selected_point(self, x_loc):
        log.debug("Drawing point at location {}".format(x_loc))
        self.RunScript("setOutline({});".format(x_loc))

    def set_center(self, **kwargs):
        self.RunScript(_setCenterScript(**kwargs))

    def _createPolylineScript(self):
        script = "var Coordinates = ["
        for item in self.geodata.raw:
            script += "new google.maps.LatLng({}, {}),".format(item[1], item[2])

        script += "];"
        script += """
         window.Path = new google.maps.Polyline({
           path: Coordinates,
           strokeColor: "#000000",
           strokeOpacity: 1.0,
           strokeWeight: 1
         });
        window.Path.setMap(window.map);
        """
        return script

    def create_polyline(self):
        self.RunScript(self._createPolylineScript())

    def update_offset(self):
        self.Reload()
        wx.FutureCall(2000, self.__initPoints)

    def _createMarkersJSON(self, locations=None):
        if locations is None:
            locations = self.geodata.interp

        ls = []
        for i, item in enumerate(locations):
            if item[1] != -200 and item[2] != -200:
                ls.append({"i": i, "lat": item[1], "lon": item[2]})
        return "var json = '{}'".format(json.dumps(ls))

    def create_markers(self, locations=None):
        self.RunScript("createMarkers("+self._createMarkersJSON(locations)+");")

    def update_current_subset(self, event=None):
        """

        :param event:
        :return:
        """
        if event.dataset.get_channel() != self.ch:
            event.Skip()
            return

        current_subset_title = event.dataset.get_title()
        self.current_channel_static_text.SetLabel("Viewing subset {}".format(current_subset_title))
        event.Skip()

    def update_colors(self, event=None):
        if event is not None:
            if hasattr(event, "temp_extents"):
                self.temp_extents = event.temp_extents
            if hasattr(event, "space_series"):
                if self._space_series_values == 'mean':
                    self.space_series = np.nanmean(event.dataset.get_array(), axis=0)
                elif self._space_series_values == 'std':
                    self.space_series = np.nanstd(event.dataset.get_array(), axis=0)
                    self.temp_extents = (np.nanmin(self.space_series), np.nanmax(self.space_series))
                elif self._space_series_values == 'max':
                    self.space_series = np.nanmax(event.dataset.get_array(), axis=0)
                elif self._space_series_values == 'min':
                    self.space_series = np.nanmin(event.dataset.get_array(), axis=0)
                else:
                    self.space_series = event.space_series
            if hasattr(event, "dataset"):
                self.offset = event.dataset.get_xmin()
        if self.space_series is not None:
            window = self.GetTopLevelParent()
            cmap = window.colors.get_colormap()
            temp_extents = window.colors.get_temp_extents()
            if temp_extents is None:
                temp_extents = np.nanmin(self.space_series), np.nanmax(self.space_series)
            if hasattr(event, "cmap"):
                cmap = event.cmap
            colors = self.get_marker_colors(temp_extents, self.space_series, cmap)
            script = self._get_color_script(colors)
            self.RunScript(script)
            log.debug("Colors updated in {} showing {}".format(self.__class__.__name__, self.ch.get_title()))

        if event:
            event.Skip()

    def _get_color_script(self, colors, locations=None):
        if locations is None:
            locations = self.geodata.interp
        script = ""
        for i, item in enumerate(locations):
            idx = i - self.offset
            if idx < 0:
                idx = None
            try:
                color = colors[idx]
            except:
                color = GRAY
            if item[1] != -200:
                script += "window.markers[{}].div_.style.backgroundColor = '{}';".format(i, color)

        return script

    def _onOffsetSet(self, event):
        log.debug("Offset Set in "+self.__class__.__name__)
        self._updatePoints(event.interpolated)
        event.Skip()

    def _updatePoints(self, locations=None):
        from html import html
        self.LoadFileString(html, self._createMarkersJSON(locations))
        wx.FutureCall(1000, self.update_colors)

    def __initScript(self):
        script = self._createMarkersJSON()
        return script

    def __fireMoveTooltipEvent(self):
        log.debug("x_loc: {0}".format(int(self.x_loc)))
        from dts.ui.evt import TooltipMovedEvent
        event = TooltipMovedEvent(-1,
                                  x_loc=self.x_loc,
                                  t_loc=None,
                                  dataset=self.ch,
                                  source=self)
        wx.PostEvent(self, event)

    def _onKey(self, evt):
        """Moves the tooltip if the arrow keys are pressed"""
        code = evt.KeyCode
        if code == wx.WXK_LEFT:
            self.x_loc -= 1
        if code == wx.WXK_RIGHT:
            self.x_loc += 1
        self.__draw_selected_point(self.x_loc)

    def _onKeyRelease(self, evt):
        """only redraw graph panel key is released (to prevent lag)"""
        self.__fireMoveTooltipEvent()

    def scpt(self, evt=None):
        self._updatePoints(update=False)

    def _on_radio_box(self, event):
        """Handles radio box event"""

        radio_box = event.GetEventObject()
        if radio_box.GetParent() is not self:
            event.Skip()
            return

        if radio_box.GetLabel() == 'Series Values':
            string_selection = radio_box.GetStringSelection()

            if string_selection == self._space_series_values:
                return
            elif string_selection == 'Inst.':
                self._space_series_values = 'inst'
            elif string_selection == 'Max':
                self._space_series_values = 'max'
            elif string_selection == 'Min':
                self._space_series_values = 'min'
            elif string_selection == 'Mean':
                self._space_series_values = 'mean'
            elif string_selection == 'Std':
                self._space_series_values = 'std'

            log.debug('Space series values updated to {}'.format(string_selection))

            self.update_colors(self._last_tooltip_move_event)

    def save_image(self):
        """

        :param path:
        :param bitmap_type:
        :return:
        """

        wildcard = 'BMP files (*.bmp)|*.bmp|PNG files (*.png)|*.png'
        path = dts.ui.dialog.file_io.save_file("Save current view as image file", wildcard)

        if path:

            _, ext = os.path.splitext(path)

            if ext == '.bmp':
                bitmap_type = wx.BITMAP_TYPE_PNG
            elif ext == '.png':
                bitmap_type = wx.BITMAP_TYPE_PNG

            size = self.web_control.Size
            context = wx.ClientDC(self.web_control)
            bmp = wx.EmptyBitmap(size.width, size.height)
            memory_dc = wx.MemoryDC()
            memory_dc.SelectObject(bmp)
            memory_dc.Blit(0, 0, size.width, size.height, context, 0, 0)
            memory_dc.SelectObject(wx.NullBitmap)
            img = bmp.ConvertToImage()
            img.SaveFile(path, bitmap_type)


class StatsGoogleMapControl(GoogleMapControl):

    def __init__(self, parent, **kwargs):

        self.ch = None
        self.geodata = None
        self.geodata_interp = None
        GoogleMapControl.__init__(self, parent, **kwargs)

    def _onTooltipMoved(self, event):

        event.Skip()

    def _init_space_series(self):
        self._space_series_values = 'max'
        return self.calc_space_series(self._space_series_values)

    def calc_space_series(self, value):

        window = self.GetTopLevelParent()
        space_series = None
        for channel_id in window.data.get_channels():
            channel_array = window.data.channels[channel_id].get_array()[:]
            if value == 'mean':
                array = np.nanmean(channel_array, axis=0)
            elif value == 'min':
                array = np.nanmin(channel_array, axis=0)
            elif value == 'std':
                array = np.nanstd(channel_array, axis=0)
            else:  # initialized as 'max'
                array = np.nanmax(channel_array, axis=0)

            if space_series is None:
                space_series = array
            else:
                space_series = np.append(space_series, array)

        return space_series

    def setupData(self):

        window = self.GetTopLevelParent()
        geodata_interp = None
        for channel_id in window.data.get_channels():
            ch = window.data.channels[channel_id]
            if not ch.geodata.loaded:
                log.error("Cannot initialize " + self.__class__.__name__ + ": geospatial data not available.")
                self.Delete()
                self.Destroy()
            if geodata_interp is None:
                geodata_interp = ch.geodata.interp
            else:
                geodata_interp = np.append(geodata_interp, ch.geodata.interp, axis=0)

        self.geodata_interp = geodata_interp

    def set_up_display(self):

        from html import html
        self.LoadFileString(html, self._createMarkersJSON(self.geodata_interp))

        sizer = self.GetSizer()

        current_channel_title = 'Multi-channel statistics'
        self.current_channel_static_text = wx.StaticText(self,
                                                         label="Showing {}".format(current_channel_title))

        sizer.Add(self.current_channel_static_text)

        radio_box_choices = ['Max', 'Min', 'Mean', 'Std']
        self.radio_box = wx.RadioBox(parent=self, style=wx.RA_SPECIFY_COLS, majorDimension=5,
                                     choices=radio_box_choices, label='Series Values')

        sizer.Add(self.radio_box, 0.1, wx.EXPAND, 0)

    def update_colors(self, event=None):

        self.space_series = self.calc_space_series(self._space_series_values)

        window = self.GetTopLevelParent()
        temp_extents = window.colors.get_temp_extents()

        if self._space_series_values == 'std' or temp_extents is None:
            temp_extents = (np.min(self.space_series), np.max(self.space_series))
        if hasattr(event, "cmap"):
            cmap = event.cmap
        else:
            cmap = window.colors.get_colormap()
        colors = self.get_marker_colors(temp_extents, self.space_series, cmap)
        script = self._get_color_script(colors, self.geodata_interp)
        self.RunScript(script)
        log.debug("Colors updated in {}".format(self.__class__.__name__))

        if event:
            event.Skip()
