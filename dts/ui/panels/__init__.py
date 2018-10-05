import wx
import logging as log
import dts


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        log.info("Loading panel {0}".format(self.__class__.__name__))
        wx.Panel.__init__(self, *args, **kwargs)

    def Delete(self):
        wx.CallAfter(self.Destroy)


class ModalPanel(Panel):
    panel = None

    def __init__(self, parent):
        Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        from dts.ui.colors import LightRed
        self.SetBackgroundColour(LightRed)
        self.Hide(False)

    def Show(self, panel):
        self.panel = panel
        self.sizer = wx.BoxSizer()
        self.sizer.Add(panel, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        Panel.Show(self)
        wx.FutureCall(1,self.Parent.Layout)

    def Hide(self, layout=True):
        Panel.Hide(self)
        if self.panel != None:
            wx.CallAfter(self.panel.Destroy)
        if layout:
            wx.FutureCall(1,self.Parent.Layout)

    def Close(self):
        self.Hide()


class NotebookChildPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        log.debug("Creating panel "+self.__class__.__name__)
        wx.Panel.__init__(self, *args, **kwargs)

    def Delete(self):
        log.debug("Deleting panel "+self.__class__.__name__)
        if self.GetParent().__class__.__name__ == "PlotNotebook":
            i = self.Parent.GetPageIndex(self)
            if i != -1:
                self.Parent.RemovePage(i)
        wx.CallAfter(self.Destroy)
        log.debug("Panel deleted.")

    def GetParentNotebook(self):
        A = self.GetParent()
        while A.__class__.__name__ != "PlotNotebook":
            A = A.GetParent()
        return A