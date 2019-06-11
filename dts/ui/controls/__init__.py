import wx
import dts
import logging as log
from dts.ui.panels import Panel


class ChannelSelectCtrl(wx.Choice):
    def __init__(self, parent):
        window = parent.GetTopLevelParent()
        channels = window.data.get_channels()
        wx.Choice.__init__(self, parent, id=wx.ID_ANY, choices=channels)

        self.Bind(wx.EVT_CHOICE, self.__onChange__)

    def __onChange__(self, event):
        sel = self.GetSelection()
        event.Skip()


class SubsetsListCtrl(wx.ListBox):
    def __init__(self, parent, **kwargs):
        self.window = parent.GetTopLevelParent()
        self.parent = parent
        self.set_control_options()

        wx.ListBox.__init__(self, parent, id=wx.ID_ANY,
                            choices=self.titles, **kwargs)
        self.Bind(wx.EVT_LISTBOX, self.__onChange__)
        self.window.Bind(dts.ui.evt.EVT_SUBSET_EDITED, self.__change_options__)
        self.window.Bind(dts.ui.evt.EVT_SUBSET_SELECTED,
                         self.__on_subset_selected)
        self.window.Bind(dts.ui.evt.EVT_SUBSET_DELETED,
                         self.__change_options__)
        if len(self.keys) > 0:
            self.set_selection(self.keys[0])

    def set_control_options(self):
        self.subsets = self.parent.ch.subsets
        items = self.subsets.items()
        self.titles = [item[1].get_title() for item in items]
        self.keys = [item[0] for item in items]

    def __change_options__(self, event=None):
        self.set_control_options()
        self.Set(self.titles)
        print "Subsets List Box updated"
        event.Skip()

    def __on_subset_selected(self, event):
        if event.subset.get_channel() is self.parent.ch:
            key = event.subset.get_key()
            self.set_selection(key)
        event.Skip()

    def set_selection(self, key):
        i = self.keys.index(key)
        self.SetSelection(i)

    def get_selection(self):
        sel = self.GetSelection()
        print "Subset selected: {}".format(sel)
        self.key = self.keys[sel]
        print self.key
        return self.subsets[self.key]

    def __onChange__(self, event):
        subset = self.get_selection()
        event = dts.ui.evt.SubsetSelectedEvent(
            wx.ID_ANY, new=False, subset=subset)
        wx.PostEvent(self, event)


class Fieldset(wx.BoxSizer, dict):
    def __init__(self, parent, label, control=None, text=None, sizer=None, **kwargs):
        """A class to simplify the construction of simple labeled fields. If a 'sizer' kwarg is specified, elements will
        be added to this sizer; otherwise, the class will act as its own sizer.
        """
        dict.__init__(self)
        if sizer is None:
            wx.BoxSizer.__init__(self, wx.VERTICAL)
            sizer = self

        labelsize = 11
        fontsize = 11
        if wx.Platform == '__WXMSW__':
            labelsize = 8
            fontsize = 12

        self.label_font = wx.Font(
            labelsize, wx.DEFAULT, wx.NORMAL, wx.BOLD, False)
        self.field_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)

        self["label"] = wx.StaticText(parent, wx.ID_ANY, label)
        self["label"].SetFont(self.label_font)

        sizer.Add(self["label"])

        if text is not None:
            self["control"] = wx.StaticText(parent, wx.ID_ANY, text)
            self["control"].SetFont(self.field_font)
        elif control is not None:
            self["control"] = control
        else:
            Exception(
                "Expected either a wxPython object (under keyword 'control') or string under keyword 'text'.")
        sizer.Add(self["control"], **kwargs)


class SubsetCtrl(Panel):
    focused = False
    last_good = None
    is_good = True
    min = 0
    max = 100

    def __init__(self, parent, formatter=None, value=0, range=(0, 100), **kwargs):
        Panel.__init__(self, parent)
        self.value = value
        if formatter is not None:
            self.formatter = formatter
        else:
            self.formatter = lambda x: "{}".format(x)
        self.__doLayout()
        self.SetRange(*range)
        self.spin.SetValue(int(self.value))
        self.__bindEvents()

    def __bindEvents(self):
        self.text.Bind(wx.EVT_TEXT, self.handle_keypress)
        self.text.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.text.Bind(wx.EVT_TEXT_ENTER, self.on_kill_focus)

        self.spin.Bind(wx.EVT_SPIN_UP, self.on_spin_up)
        self.spin.Bind(wx.EVT_SPIN_DOWN, self.on_spin_down)

    def __doLayout(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, value=self.formatter(
            self.value), style=wx.TE_PROCESS_ENTER)
        self.sizer.Add(self.text)

        self.spin = wx.SpinButton(self, style=wx.SP_VERTICAL, size=(16, 22))
        self.sizer.Add(self.spin)

        self.SetSizer(self.sizer)

    def SetValue(self, value):
        if value < self.GetMin():
            value = self.GetMin()
        if value > self.GetMax():
            value = self.GetMax()
        self.value = value
        self.spin.SetValue(value)
        if not self.focused and self.formatter is not None:
            value = self.formatter(value)
        self.text.SetValue("{}".format(value))
        event = dts.ui.evt.ValueUpdatedEvent(-1,
                                             value=self.GetValue(), source=self)
        wx.PostEvent(self, event)

    def GetValue(self):
        return self.value

    def SetRange(self, *args):
        self.spin.SetRange(*args)

    def SetMin(self, min):
        self.spin.SetMin()

    def SetMax(self, max):
        self.spin.SetMax()

    def GetMin(self):
        return self.spin.GetMin()

    def GetMax(self):
        return self.spin.GetMax()

    def SetValueString(self, value):
        self.text.SetValue(value)

    def GetValueString(self):
        return self.text.GetValue()

    def on_spin_up(self, evt):
        self.SetValue(self.value + 1)

    def on_spin_down(self, evt):
        self.SetValue(self.value - 1)

    def on_set_focus(self, evt):
        self.last_good = self.GetValue()
        self.focused = True
        self.SetValueString("{0}".format(self.GetValue()))
        evt.Skip()

    def on_kill_focus(self, evt):
        if self.focused is False:
            return
        if self.is_good:
            i = int(self.GetValueString())
        else:
            log.debug("Changing from bad value")
            i = self.last_good
            self.text.SetBackgroundColour("white")
            self.is_good = True
        self.focused = False
        self.SetValue(i)
        evt.Skip()

    def handle_keypress(self, event):
        if not self.focused:
            return
        try:
            int(self.GetValueString())
            self.is_good = True
            self.text.SetBackgroundColour("white")
        except ValueError:
            self.is_good = False
            self.text.SetBackgroundColour("pink")

        event.Skip()
