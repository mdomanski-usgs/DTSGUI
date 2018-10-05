import wx
import dts
import dts.ui.evt as evt
import logging as log
from dts.ui.panels import NotebookChildPanel as Panel
from dts.ui.plot import PlotImage
from range_control import SpaceRangeControl, TimeRangeControl
from dts.ui.controls import Fieldset


class SubsetEditor(Panel):
    def __init__(self, parent, subset=None):
        Panel.__init__(self, parent, id=-1, style=wx.EXPAND | wx.GROW)
        self.subset = subset
        if subset != None:
            self.add_new = False
        else:
            self.add_new = True

        self.__doLayout()

    def __doLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.plot = PlotImage(self)
        self.cpanel = SubsetCtrlPanel(self, self.subset)

        sizer.Add(self.cpanel, 0, wx.EXPAND)
        sizer.Add(self.plot, 1, wx.EXPAND | wx.GROW | wx.ALL, 0)

        self.SetSizer(sizer)

    def Destroy(self, *args, **kwargs):
        log.debug("Destroying {}".format(self.__class__.__name__))
        self.cpanel.Destroy()
        self.plot.Destroy()
        Panel.Destroy(self)

    def update(self):
        pass


class ExtentsCtrlPanel(Panel):
    def __init__(self, parent, button_label = "Save Subset", subset=None, dataset=None):
        Panel.__init__(self,parent, id=wx.ID_ANY, size=(150,-1))
        self.__update_data(dataset)
        self.__create_extents(subset)
        self.__layout(button_label)
        self.parent = parent

    def __create_extents(self, subset):
        self.subset = subset
        if subset == None:
            self.extents = {
                "time": None,
                "space": None
            }
        else:
            self.extents = subset.get_bounds(format="timespace")
            print self.extents

    def __layout(self, button_label):
        self.sizer = wx.GridBagSizer()
        self.sizer.SetFlexibleDirection(wx.BOTH)

        self.sizer.AddGrowableCol(0)
        self.SetSizer(self.sizer)

        self.__extentControls()
        self.__buttonControls(button_label)

    def __update_data(self, dataset):
        if not hasattr(self, "data"):
            if dataset is None:
                window = self.GetTopLevelParent()
                self.channel = window.status.get_current_channel()
                self.data = self.channel.data
            else:
                self.data = dataset

    def __extentControls(self):
        print self.extents
        self.space = SpaceRangeControl(self,"Distance Range", data=self.data, extents=self.extents["space"])
        self.time = TimeRangeControl(self,"Time Range", data=self.data, extents=self.extents["time"])

        self.extents = {
            "space": {
                "min": self.space.get_min(),
                "max": self.space.get_max()
            },
            "time": {
                "min": self.time.get_min(),
                "max": self.time.get_max()
            }
        }

        for i,key in enumerate(["space", "time"]):
            self.sizer.Add(getattr(self, key), wx.GBPosition(0,i+1), wx.GBSpan(1,1), wx.EXPAND|wx.GROW)

        self.Bind(dts.ui.evt.EVT_VALUE_UPDATED, self.on_spin)
        self.Parent.plot.plot_box(self.extents)

    def on_spin(self, evt):
        value = evt.Int
        for name in ["time", "space"]:
            rngCtrl = getattr(self, name)
            self.extents[name] = rngCtrl.get_extents()
        self.Parent.plot.plot_box(self.extents)

    def __buttonControls(self, main_button_label="Save Subset"):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.buttons = {}
        self.buttons["extents"] = wx.Button(self, -1, 'Set Bounds to View Extents')
        self.buttons["accept"] = wx.Button(self, -1, main_button_label)
        self.buttons["cancel"] = wx.Button(self, -1, 'Cancel')

        for item in ["extents","accept", "cancel"]:
            button_sizer.Add(self.buttons[item], 0, wx.ALIGN_RIGHT|wx.LEFT, 5)

        self.sizer.Add(button_sizer, wx.GBPosition(1,0), wx.GBSpan(1,3), wx.ALIGN_RIGHT| wx.ALL, border=5)

        self.Bind(wx.EVT_BUTTON, self.on_accept, id=self.buttons["accept"].GetId())
        self.Bind(wx.EVT_BUTTON, self.on_set_extents, id=self.buttons["extents"].GetId())
        self.Bind(wx.EVT_BUTTON, self.on_cancel, id=self.buttons["cancel"].GetId())

    def on_accept(self, evt):
        extents = self.get_xy_extents()
        #print extents
        log.info("Subset edited.")
        #self.channel.trim_raw(**extents)
        self.on_cancel(evt)

    def on_cancel(self, evt):
        wx.CallAfter(self.Parent.Delete)

    def get_xy_extents(self):
        return dict(
            x_min = self.extents['space']['min'],
            x_max = self.extents['space']['max'],
            t_min = self.extents['time']['min'],
            t_max = self.extents['time']['max']
            )

    def set_button_active(self, active=True):
        """This sets the accept button (sublcassed to 'Create subset' or 'Trim raw data') to 'greyed-out' or active"""
        pass

    def on_set_extents(self, evt):
        ax = self.Parent.plot.ax
        xb = ax.get_xbound()
        yb = ax.get_ybound()

        for bounds, label in zip((xb, yb), ('space','time')):
            min, max = bounds
            min = int(round(min+.5))
            max = int(round(max-.5))
            self.extents[label] = {'min': min, 'max': max}

            control = getattr(self,label)
            control.set_extents(self.extents[label])
        print self.extents
        self.Parent.plot.plot_box(self.extents)

    def GetParentNotebook(self):
        A = self.GetParent()
        while A.__class__.__name__ != "PlotNotebook":
            A = A.GetParent()
        return A


class SubsetCtrlPanel(ExtentsCtrlPanel):
    def __init__(self, parent, subset=None):
        self.subset = subset
        self.title_changed = False
        if self.subset is None:
            btnText = "Create Subset"
            self.title = wx.EmptyString
            self.description = wx.EmptyString
            self.new = True
        else:
            btnText = "Save Subset"
            self.new = False
            self.title = self.subset.get_title()
            self.description = self.subset.get_description()
        ExtentsCtrlPanel.__init__(self, parent, btnText, subset=self.subset)
        self.window = self.GetTopLevelParent()
        self.__textControls()

    def __textControls(self):
        insizer = wx.BoxSizer(wx.VERTICAL)

        self.title_ctrl = Fieldset(self, "Title", control=wx.TextCtrl(self, value=self.title), flag=wx.EXPAND)
        insizer.Add(self.title_ctrl, 0, wx.EXPAND|wx.ALL, 0)
        self.title_ctrl["control"].Bind(wx.EVT_TEXT, self.update_title)

        self.desc_ctrl = Fieldset(self, "Description", wx.TextCtrl(self, value=self.description, style=wx.TE_MULTILINE), proportion=1, flag=wx.EXPAND|wx.GROW)
        insizer.Add(self.desc_ctrl, 1, wx.EXPAND|wx.GROW|wx.TOP, 5)
        self.desc_ctrl["control"].Bind(wx.EVT_TEXT, self.update_description)

        self.sizer.Add(insizer, wx.GBPosition(0,0), None, wx.EXPAND|wx.GROW|wx.ALL, 5)

    def update_title(self, evt):
        string = evt.GetString()
        if string != self.title: self.title_changed = True
        if string == '':
            self.title = wx.EmptyString
        else:
            self.title = string

    def update_description(self, evt):
        string = evt.GetString()
        if string == '':
            self.description = wx.EmptyString
        else:
            self.description = string

    def on_accept(self, event):
        extents = self.get_xy_extents()
        #print extents
        subsets = self.window.status.current_channel.subsets
        window = self.GetTopLevelParent()

        if self.title == wx.EmptyString:
            dlg = wx.MessageDialog(window,
            "Please set a title before continuing.",
            'Title not set',
            wx.OK|wx.ICON_ASTERISK)
            do_it = dlg.ShowModal()
            dlg.Destroy()
            if do_it != wx.ID_YES:
                return None

        if self.new is True:
            self.subset = subsets.create_new(self.title.encode())
        elif self.title_changed is True:
            self.subset.set_title(self.title.encode())
        self.subset.set_description(self.description.encode())
        self.subset.set_bounds(**extents)

        import dts.ui.evt as evt
        newevent = evt.SubsetEditedEvent(wx.ID_ANY, new=self.new, subset=self.subset)
        wx.PostEvent(self, newevent)
        self.on_cancel(event)
