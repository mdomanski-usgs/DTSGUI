import wx
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
import logging as log
from dts.ui.panels import Panel
from dts.ui import ButtonFont

temp_format = "{0:.1f}"


class ToolBarBase(object):
    def add_ctrl(self, control=wx.TextCtrl, label=None, format_string=temp_format, size=40, init_val=1):
        try:
            init_val = format_string.format(init_val)
        except:
            pass
        if label is not None:
            lbl = wx.StaticText(self, (-1, 28), label)
            self.AddControl(lbl)
        # allows the processing of enter commands while the focus is on the control
        ctrl = control(self, -1, init_val, size=(size, 26), style=wx.TE_PROCESS_ENTER | wx.TAB_TRAVERSAL)
        self.AddControl(ctrl)
        return ctrl

    def add_chkbox(self, label):
        ctrl = wx.CheckBox(self, -1, label)
        self.AddControl(ctrl)
        return ctrl


class ColorbarExtentsControl(Panel):
    temp_format = "{0:.1f}"

    def __init__(self, parent, range=None):
        Panel.__init__(self, parent)

        self.plot = self.Parent.Parent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.controls = {}
        if range is None:
            range = self.plot.data.get_temp_range()
        kwargs = dict(size=(50, -1))
        self.controls["min"] = wx.TextCtrl(self, -1, **kwargs)
        self.controls["max"] = wx.TextCtrl(self, -1, **kwargs)

        self.set_min(range[0])
        self.set_max(range[1])
        for key in ['min', 'max']:
            ctrl = self.controls[key]
            self.sizer.Add(ctrl, 0, wx.LEFT, 5)
            ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_set_limits)
            ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_set_limits)

        auto = wx.Button(self, label='Auto')
        auto.SetFont(ButtonFont())
        self.sizer.Add(auto, 0, wx.LEFT, 5)
        auto.Bind(wx.EVT_BUTTON, self.on_auto_clim)
        auto.Disable()
        self.controls["auto"] = auto
        self.SetSizer(self.sizer)

    def set_auto_clim(self):
        try:
            # if min != self.min or max != self.max and not self.plot.temp_extents_autoset():
            if not self.plot.temp_extents_autoset():
                self.controls["auto"].Enable()
            else:
                self.controls["auto"].Disable()
        except AttributeError:
            pass
        except KeyError:
            pass

    def get_min(self):
        try:
            return float(self.controls["min"].GetValue())
        except ValueError:
            self.set_min()
            return self.min

    def get_max(self):
        try:
            return float(self.controls["max"].GetValue())
        except ValueError:
            self.set_max()
            return self.max

    def set_min(self, value):
        value = float(value)
        self.min = value
        self.controls['min'].SetValue(self.temp_format.format(value))
        self.set_auto_clim()

    def set_max(self, value):
        value = float(value)
        self.max = value
        self.controls['max'].SetValue(self.temp_format.format(value))
        self.set_auto_clim()

    def on_set_limits(self, evt):
        min = self.get_min()
        max = self.get_max()

        try:
            self.plot.set_temp_extents(min, max)
        except ValueError:
            log.debug("Min must be less than max.")
            self.set_min(max)
            self.set_max(min)
            self.plot.set_temp_extents(max, min)

        self.set_auto_clim()

        evt.Skip()

    def on_auto_clim(self, evt):
        temps = self.plot.data.get_temp_range()
        min, max = [float(i) for i in temps]
        log.debug("Autoset colorbar extents to ({0:.1f}, {1:.2f})".format(min, max))
        self.plot.set_temp_extents(min, max)
        self.set_min(min)
        self.set_max(max)

        self.set_auto_clim()


class DisplayOptionsToolbar(Panel, ToolBarBase):
    def __init__(self, parent):
        Panel.__init__(self, parent, size=(-1, 36))
        self.window = self.GetTopLevelParent()
        from dts.ui.colors import LightRed
        self.SetBackgroundColour(LightRed)
        outsizer = wx.BoxSizer()
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.StaticText(self, -1, 'Colormap\nLimits', size=(-1, 30), style=wx.ALIGN_RIGHT | wx.TB_NODIVIDER)
        txt.SetFont(ButtonFont())
        self.AddControl(txt, 0, wx.TOP, 3)

        temp_extents = self.window.colors.get_temp_extents()
        self.cbar_extents = ColorbarExtentsControl(self, temp_extents)
        self.AddControl(self.cbar_extents, 0, wx.TOP | wx.RIGHT, 5)

        txt = wx.StaticText(self, -1, 'Subplot\nVisibility', style=wx.ALIGN_RIGHT)
        txt.SetFont(ButtonFont())
        self.AddControl(txt, 0, wx.TOP | wx.LEFT, 3)

        self.subplots = dict()
        self.subplots['cbar'] = self.add_chkbox('Colorbar')
        self.subplots['t_ax'] = self.add_chkbox('Time')
        self.subplots['c_ax'] = self.add_chkbox('Cable')

        for key in ["t_ax", "c_ax"]:
            self.subplots[key].SetValue(True)

        outsizer.Add(self.sizer, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(outsizer)  # This is necessary to bind the controls to the frame. Necessary on windows.

        self.Hide()
        self.Parent.sizer.Add(self, 0, wx.EXPAND | wx.GROW)

    def add_chkbox(self, label):
        ctrl = wx.CheckBox(self, -1, label)
        self.AddControl(ctrl, 0, wx.TOP | wx.LEFT, 10)
        return ctrl

    def AddControl(self, *args, **kwargs):
        self.sizer.Add(*args, **kwargs)


class MainPlotToolbar(Toolbar, ToolBarBase):
    def __init__(self, parent):
        Toolbar.__init__(self, parent)

        SUBPLOTS_BTN = 6
        self.DeleteToolByPos(SUBPLOTS_BTN)

        self.AddSeparator()

        # self.displayOptions = self.Parent.displayOptions

        control = wx.Button(self, label='Show Display Options')
        size = 10
        if wx.Platform == "__WXMSW__":
            size = 8
        control.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.AddControl(control)
        control.Bind(wx.EVT_BUTTON, self._toggleDisplayOptions)

        self.AddSeparator()

        self.params = dict()
        self.params['minmax'] = self.add_chkbox('Min/Max')
        self.params['mean'] = self.add_chkbox('Mean')
        self.params['std'] = self.add_chkbox('Std dev')

    def _toggleDisplayOptions(self, evt):
        button = evt.EventObject
        if self.Parent.displayOptions.IsShown():
            button.SetLabel('Show Display Options')
            self.Parent.displayOptions.Hide()
        else:
            button.SetLabel('Hide Display Options')
            self.Parent.displayOptions.Show()
        self.Parent.Layout()
        # self.Parent.sizer.RecalcSizes()

    def home(self, *args):

        self.Parent._SetSize()
        Toolbar.home(self, *args)
