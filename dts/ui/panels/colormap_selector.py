import wx
import numpy as np
import matplotlib as mpl
from dts.ui.evt import ColormapChangedEvent
from dts.ui.controls import Fieldset


from wx.lib.scrolledpanel import ScrolledPanel


class ColormapSelector(ScrolledPanel):
    def __init__(self, parent, name="right"):
        ScrolledPanel.__init__(self, parent)
        self.window = self.GetTopLevelParent()
        self.SetupScrolling()
        self.__draw()

        self.Bind(wx.EVT_BUTTON, self.on_colormap_selected)

    def __draw(self):

        outsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(outsizer)

        a = np.outer(np.ones(10), np.arange(0, 1, 0.01))

        maps = ['jet']
        maps.extend(list(mpl.cm.cmaps_listed.keys()))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.controls = {}

        for name in maps:
            fig = mpl.figure.Figure(figsize=(5, .5), dpi=72)
            from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
            canvas = FigureCanvas(fig)

            fig.ax = fig.add_axes((0, 0, 1, 1))
            fig.ax.imshow(a, aspect='auto', cmap=getattr(mpl.cm, name), origin="lower")
            fig.ax.set_axis_off()

            canvas.draw()
            rgb = canvas.tostring_rgb()
            Image = wx.EmptyImage(*canvas.get_width_height())
            Image.SetData(rgb)

            button = wx.BitmapButton(self, wx.ID_ANY, Image.ConvertToBitmap(), name=name)

            ctrl = Fieldset(self, self._label(name), control=button)
            self.controls[name] = ctrl
            sizer.Add(ctrl, 0, wx.TOP, 5)

        outsizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 10)

    def on_colormap_selected(self, event):
        name = event.EventObject.GetName()
        current = self.window.colors.current_cmap.name
        self.controls[current]['label'].SetLabel(self._label(current, False))

        if name != current:
            colormap = mpl.cm.__dict__[name]
            event = ColormapChangedEvent(-1, cmap=colormap)
            wx.PostEvent(self, event)

            self.controls[name]['label'].SetLabel(self._label(name, True))

    def _label(self, name, current=None):
        C = self.window.colors
        text = ""
        if name == C.current_cmap.name:
            if current is not False:
                text += " (Currently selected)"
        elif current:
            text += " (Currently selected)"
        if name == C.default_cmap.name:
            text += " (Default)"
        return name+text
