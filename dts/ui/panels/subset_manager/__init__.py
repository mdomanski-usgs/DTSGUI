import wx
import dts
from dts.ui.plot import PlotImage
from dts.ui.controls import Fieldset, SubsetsListCtrl, ChannelSelectCtrl
from dts.ui.controls.web import CPL_WebControl
import dts.ui.evt as evt
import logging as log
import datetime
from matplotlib.patches import Rectangle


class SubsetManager(dts.ui.panels.NotebookChildPanel):
    def __init__(self, parent, id=wx.ID_ANY):
        dts.ui.panels.NotebookChildPanel.__init__(self, parent, id, style=wx.EXPAND)
        window = self.GetTopLevelParent()
        self.ch = window.data.ch
        self.controls = SubsetManagerControls(self)

        self.plot = SubsetGraphPanel(self, self.controls.get_subset())
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.controls, 0, wx.EXPAND | wx.ALL)
        main_sizer.Add(self.plot, 1, wx.EXPAND |wx.ALL)
        self.SetSizer(main_sizer)

    def Destroy(self, *args, **kwargs):
        log.debug("Destroying {}".format(self.__class__.__name__))
        self.controls.Destroy()
        self.plot.Destroy()
        super(dts.ui.panels.NotebookChildPanel, self).Destroy(*args, **kwargs)


class SubsetManagerControls(dts.ui.panels.NotebookChildPanel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.EXPAND | wx.ALL)

        self.ch = parent.ch

        sizer = wx.GridBagSizer()
        sizer.SetFlexibleDirection(wx.BOTH)
        sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.subset_selector = Fieldset(self, "Select subset", control=SubsetsListCtrl(self, size=(150, -1)))
        sizer.Add(self.subset_selector, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND | wx.ALL, 5)

        self.buttons = {'add_subset': wx.Button(self, wx.ID_ANY, u"Add Subset \u00BB")}
        sizer.Add(self.buttons["add_subset"], wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.description_panel = DescriptionPanel(self, self.get_subset())
        sizer.Add(self.description_panel, wx.GBPosition(0, 1), wx.GBSpan(2, 1),
                  wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, 5)

        bSizer7 = wx.BoxSizer(wx.VERTICAL)

        self.buttons["view_subset"] = wx.Button(self, wx.ID_ANY, u"View Subset")
        bSizer7.Add(self.buttons["view_subset"], 0, wx.EXPAND | wx.TOP, 5)

        self.buttons["edit_subset"] = wx.Button(self, wx.ID_ANY, u"Edit Subset")
        bSizer7.Add(self.buttons["edit_subset"], 0, wx.EXPAND | wx.TOP, 5)

        self.buttons["delete_subset"] = wx.Button(self, wx.ID_ANY, u"Delete Subset")
        bSizer7.Add(self.buttons["delete_subset"], 0, wx.EXPAND | wx.TOP, 5)

        sizer.Add(bSizer7, wx.GBPosition(0, 2), wx.GBSpan(2, 1), wx.ALIGN_RIGHT | wx.ALL, 5)

        sizer.AddGrowableCol(1)

        self.SetSizer(sizer)

        self.buttons["add_subset"].Bind(wx.EVT_BUTTON, self.on_new_subset)
        self.buttons["view_subset"].Bind(wx.EVT_BUTTON, self.on_view_subset)
        self.buttons["edit_subset"].Bind(wx.EVT_BUTTON, self.on_edit_subset)
        self.buttons["delete_subset"].Bind(wx.EVT_BUTTON, self.on_delete_subset)

    def get_subset(self):
        try:
            return self.subset_selector['control'].get_selection()
        except:
            return None

    def on_view_subset(self, event):
        subset = self.get_subset()
        self.GetParentNotebook().add_main(subset)

    def on_edit_subset(self, event):
        subset = self.get_subset()
        if subset is None:
            return
        log.debug("Subset editor requested.")
        nb = self.GetParentNotebook()
        nb.add_subset_editor(subset)
        nb.SetSelection(-1)

    def on_delete_subset(self, event):
        subset = self.get_subset()
        if subset is None:
            return
        # key = subset['key']
        subsets = subset.get_channel().subsets
        key = subset.get_key()
        subset = subsets[key]
        dlg = wx.MessageDialog(self,
                               "Are you sure you want to delete the subset with name '{}'?".format(subset.get_title()),
                               'Delete subset',
                               wx.YES_NO | wx.ICON_QUESTION)
        toDo = dlg.ShowModal()
        dlg.Destroy()
        if toDo == wx.ID_YES:
            del(subsets[key])
            del(subsets.__hdf__[key])
            event = evt.SubsetDeletedEvent(wx.ID_ANY, key=key, subset=subset)
            wx.PostEvent(self, event)
            print self.GetTopLevelParent().status.current_channel.subsets

    def on_new_subset(self, event):
        self.GetParentNotebook().add_subset_editor()

    def Destroy(self, *args, **kwargs):
        log.debug("Destroying {}".format(self.__class__.__name__))
        super(dts.ui.panels.NotebookChildPanel, self).Destroy(*args, **kwargs)


class DescriptionPanel(CPL_WebControl):
    default = "---"
    vars = dict(bkg_color="#dddddd",
                name="No subset selected.",
                description=None,
                x_min=None,
                x_max=None,
                x_delta=None,
                t_min=None,
                t_max=None,
                t_delta=None,
                min=None,
                max=None,
                mean=None,
                std=None
                )
    selected = None

    def __init__(self, parent, subset=None):
        CPL_WebControl.__init__(self, parent)

        self.window = self.Parent.GetTopLevelParent()
        self.window.Bind(evt.EVT_SUBSET_SELECTED, self.on_subset_selected)
        self.window.Bind(evt.EVT_SUBSET_EDITED, self.on_subset_edited)
        self.window.Bind(evt.EVT_SUBSET_DELETED, self.on_subset_deleted)

        if subset is not None:
            self.display_info(subset)
        else:
            self.display_template()

    def display_template(self, vars=None):
        if vars is None:
            vars = self.vars

        import attributes_panel as a
        tpl = a.attributes % vars
        self.LoadSource(tpl)

    def define_background_color(self):
        bkg_color = self.Parent.GetBackgroundColour().Get()
        return '#%02x%02x%02x' % bkg_color

    def on_subset_edited(self, event):
        if self.selected is event.subset:
            self.on_subset_selected(event)
        event.Skip()

    def on_subset_deleted(self, event):
        self.selected = None
        self.display_template(DescriptionPanel.vars)
        event.Skip()

    def on_subset_selected(self, event=None):
        subset = event.subset
        self.display_info(subset)
        event.Skip()

    def display_info(self, subset):
        self.selected = subset
        self.vars['name'] = subset.get_title()
        self.vars['description'] = subset.get_description()

        x_min, x_max = subset.get_distance_interval()
        x_delta = x_max - x_min
        for i in ["x_min", "x_max", "x_delta"]:
            self.vars[i] = "{0:.2f} m".format(locals()[i])

        times = subset.get_time_range()
        time_format = dts.ui.time_format.get_format(linebreak=False)
        for time, label in zip(times, ['t_min', 't_max']):
            date = datetime.datetime.fromtimestamp(time)
            self.vars[label] = date.strftime(time_format)

        t_delta = datetime.timedelta(seconds=times[1]-times[0])
        self.vars['t_delta'] = str(t_delta)

        data = subset.get_data()

        for i in ['min', 'max', 'mean', 'std']:
            self.vars[i] = self.format_temp(getattr(data, i)())

        self.display_template()

    def format_temp(self, value=None):
        if value is None:
            return self.default
        else:
            return u"{0:.2f} \u00b0C".format(float(value))


class SubsetListPanel(dts.ui.panels.NotebookChildPanel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND | wx.GROW)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ch_change = ChannelSelectCtrl(self)
        self.subsets_list = SubsetsListCtrl(self)
        self.add_subset_button = wx.Button(self, wx.ID_ANY, "Add New" )
        self.add_subset_button.Bind(wx.EVT_BUTTON, self.on_new_subset)

        panels = [self.ch_change, self.subsets_list, self.add_subset_button]
        [sizer.Add(s, 0, wx.EXPAND | wx.ALL, 10) for s in panels]
        self.SetSizer(sizer)

    def on_new_subset(self, event):
        notebook = self.GetParentNotebook()
        notebook.add_subset_editor()


class SubsetGraphPanel(PlotImage):
    selected = None

    def __init__(self, parent, subset=None):
        PlotImage.__init__(self, parent, parent.ch)
        self.channel = parent.ch

        self.rectangles = {}
        self.__draw_subsets__()

        window = self.GetTopLevelParent()
        window.Bind(evt.EVT_SUBSET_EDITED, self.on_subset_edited)
        window.Bind(evt.EVT_SUBSET_DELETED, self.on_subset_deleted)
        window.Bind(evt.EVT_SUBSET_SELECTED, self.on_subset_selected)
        self.canvas.mpl_connect('pick_event', self.on_pick)

        if subset is not None:
            self.fill_rectangle(subset)

    def __draw_subsets__(self):
        for key, subset in self.dataset.subsets.items():
            self.__make_rectangle__(subset)
        self.canvas.draw()

    def __make_rectangle__(self, subset):
        extents = subset.get_bounds("timespace")
        key = subset.get_key()
        log.debug(extents)

        rect = self.plot_rectangle(extents)
        rect.key = key
        # This code could be changed to adjust size of rectangle instead of removing and recreating.
        if key in self.rectangles:
            self.ax.patches.remove(self.rectangles[key])
        self.rectangles[key] = self.ax.add_patch(rect)
        # self.rectangles[key]

    def _unbind_events(self):

        window = self.GetTopLevelParent()

        window.Unbind(evt.EVT_SUBSET_EDITED, handler=self.on_subset_deleted)
        window.Unbind(evt.EVT_SUBSET_DELETED, handler=self.on_subset_deleted)
        window.Unbind(evt.EVT_SUBSET_SELECTED, handler=self.on_subset_selected)

    def Destroy(self, *args, **kwargs):
        self._unbind_events()
        log.debug("Destroying {}".format(self.__class__.__name__))
        PlotImage.Destroy(self)

    def on_pick(self, event):
        if isinstance(event.artist, Rectangle):
            rect = event.artist
            key = rect.key

            subset = self.channel.subsets[key]

            log.info("Subset "+key+" selected.")

            event = dts.ui.evt.SubsetSelectedEvent(wx.ID_ANY, new=False, subset=subset)
            wx.PostEvent(self, event)

    def on_subset_selected(self, event):
        if event.subset.get_channel() is self.channel:
            self.fill_rectangle(event.subset)
        event.Skip()

    def fill_rectangle(self, subset):
        key = subset.get_key()
        rect = self.rectangles[key]
        if self.selected is not None:
            self.selected.set_facecolor('none')
        rect.set_facecolor((1.0, 1.0, 1.0, .2))
        self.selected = rect
        self.canvas.draw()

    def on_subset_edited(self, event):
        self.__make_rectangle__(event.subset)
        self.canvas.draw()
        event.Skip()

    def on_subset_deleted(self, event):
        if event.subset.get_channel() is self.channel:
            key = event.key
            # This code could be changed to adjust size of rectangle instead of removing and recreating.
            if key in self.rectangles:
                self.ax.patches.remove(self.rectangles[key])
            del(self.rectangles[key])
            self.canvas.draw()
        event.Skip()
