import wx
import dts
from dts.ui.tabs import PlotNotebook
from menu import MenuBar
from dts.ui import ColorManager, WindowStateManager
import logging as log
from dts.ui.panels import Panel, ModalPanel


class WindowModal(ModalPanel):
    def set_interval_offset(self):
        from dts.ui.panels.set_interval_offset import OffsetPanel
        page = OffsetPanel(self)
        self.Show(page)


class MainPanel(Panel):
    def __init__(self, parent):
        """"""
        Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        parent.modal_header = WindowModal(self)
        # create the AuiNotebook instance
        parent.tabs = PlotNotebook(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(parent.modal_header, 0, wx.EXPAND)
        sizer.Add(parent.tabs, 1, wx.EXPAND)
        self.SetSizer(sizer)


class GraphFrame(wx.Frame):
    """The main window of the application"""
    title = 'Distributed temperature sensor GUI'

    def __init__(self, app):
        wx.Frame.__init__(self, None, -1, self.title, size=(800,600))
        dts.ui.window = self
        self.SetSizeHints(480, 480, -1, -1)  # Window minimum size

        self.parent = app
        self.data = app.get_data()

        self.colors = ColorManager(self)
        self.status = WindowStateManager(self)

        self.menubar = MenuBar(self)

        self.main = MainPanel(self)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def GetApplication(self):
        return self.parent

    def on_explore_data(self, event):
        self.tabs.add_data_explorer()

    def on_create_channel(self, event):
        self.data.create_channel()

    def on_trim_data(self, event):
        self.tabs.add_trim_raw()
        """		from dts.ui.dialog.trim import TrimDialog

        trim = TrimDialog(self, -1, 'Trim data', self.channel)
        if trim.ShowModal() == wx.ID_OK:
        pass
        # 		if chgdep.trim:
        # 			self.data.trim_raw(**chgdep.values)
        # 			self.graph_panel.update_pages()

        chgdep.Destroy()"""

    def on_new_subset(self, event):
        self.tabs.add_subset_editor()

    def on_set_colormap(self, event):
        from dts.ui.panels.colormap_selector import ColormapSelector
        parent = dts.ui.tabset
        page = ColormapSelector(parent)
        parent.AddPage(page, "Colormap Selector")

    def save_data(self, event):
        #if self.data.is_temporary(): self.save_data_as()
        #else: self.data.save()
        self.data.save()

    def save_data_as(self, event=None):
        wildcard = "DTS GUI file (*.dts)|*.dts|"
        path = dts.ui.dialog.file_io.save_file("Create a DTS GUI file for imported data:",
                                               wildcard
                                               )
        self.data.change_filename(path)

    def on_close(self, evt):
        dlg = wx.MessageDialog(self,
                               "Do you want to save your data?",
                               'You are exiting DTS-GUI.',
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        toDo = dlg.ShowModal()
        dlg.Destroy()
        if toDo == wx.ID_YES:
            self.data.close()
            evt.Skip()
            #self.Close(True)
            self.Destroy()
        elif toDo == wx.ID_NO:
            self.Destroy()
        else:
            log.info("Escape Thwarted")

    def save_active_data_as_csv(self, channel=None):

        if channel is None:
            channel = self.status.current_channel

        subset_list = [channel.get_title()]
        subsets = channel.get_subsets()
        subset_list.extend(subsets.keys())

        with wx.SingleChoiceDialog(self, "Choose a subset to export", "Choose a subset", subset_list,
                                   wx.CHOICEDLG_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    data = channel.data
                else:
                    subset = dlg.GetStringSelection()
                    data = channel.subsets[subset]

                print data.get_title()

                wildcard = 'CSV file (*.csv)|*.csv|'
                path = dts.ui.dialog.file_io.save_file("Save active data as a CSV file:", wildcard)

                if path:
                    data.to_csv(path)

    def save_active_data_stats(self, channel=None):

        if channel is None:
            channel = self.status.current_channel

        subset_list = [channel.get_title()]
        subsets = channel.get_subsets()
        subset_list.extend(subsets.keys())

        with wx.SingleChoiceDialog(self, "Choose a subset to export", "Choose a subset", subset_list,
                                   wx.CHOICEDLG_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    data = channel.data
                else:
                    subset = dlg.GetStringSelection()
                    data = channel.subsets[subset]

                print data.get_title()

                wildcard = 'CSV file (*.csv)|*.csv|'
                path = dts.ui.dialog.file_io.save_file("Save active data statistics as a CSV file:", wildcard)

                if path:
                    data.stats_to_csv(path)

    def on_save_image(self, event=None):
        """

        :param event:
        :return:
        """
        current_page = self.tabs.get_current_page()

        try:
            current_page.save_image()
        except AttributeError:
            with wx.MessageDialog(self, "Unable to save an image of current page", caption="Unable to save image",
                                  style=wx.ICON_ERROR) as msg_dlg:
                msg_dlg.CenterOnParent()
                msg_dlg.ShowModal()

    def update_menu_bar(self, event=None):
        """

        :param event:
        :return:
        """
        if hasattr(self, 'tabs'):
            current_page = self.tabs.get_current_page()
            save_image_menu_item_id = self.menubar.FindMenuItem('File', 'Save image')
            save_image_menu_item = self.menubar.FindItemById(save_image_menu_item_id)
            if hasattr(current_page, 'save_image'):
                save_image_menu_item.Enable(True)
            else:
                save_image_menu_item.Enable(False)
