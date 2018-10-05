import wx
import wx.html2
from wx.html2 import WebView

import logging as log


class CPL_WebControl(wx.Window):

    def __init__(self, parent, url=None):

        wx.Window.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.web_control = WebView.New(self)
        sizer.Add(self.web_control, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)

        self.web_control.Bind(wx.html2.EVT_WEBVIEW_ERROR, self._handle_web_view_event)
        self.web_control.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._handle_web_view_event)
        self.web_control.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self._handle_web_view_event)
        self.web_control.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self._handle_web_view_event)

        if url is not None:
            self.web_control.LoadURL(url)

    def _handle_web_view_event(self, evt):
        """Handle web view events"""
        events = {wx.html2.EVT_WEBVIEW_ERROR.typeId: 'wx.html2.EVT_WEBVIEW_ERROR',
                  wx.html2.EVT_WEBVIEW_LOADED.typeId: 'wx.html2.EVT_WEBVIEW_LOADED',
                  wx.html2.EVT_WEBVIEW_NAVIGATED.typeId: 'wx.html2.EVT_WEBVIEW_NAVIGATED',
                  wx.html2.EVT_WEBVIEW_NAVIGATING.typeId: 'wx.html2.EVT_WEBVIEW_NAVIGATING'}
        event_type = evt.GetEventType()
        try:
            event_name = events[event_type]
        except KeyError:
            event_name = 'WebView event of type {0}'.format(event_type)
        log.debug("{} occurred".format(event_name))

    # def Bind(self, *args, **kwargs):
    #     return self.web_control.Bind(*args, **kwargs)

    def LoadFile(self, filename, script=None):
        page = unicode(open(filename, 'r').read())
        self.LoadFileString(page, script)

    def LoadFileString(self, page, script=None):
        if script is not None:
            #pass
            pagelist = page.split("</body>")
            pagelist = [pagelist[0], "<script type='text/javascript'>",  script, "</script></body>", pagelist[1]]
            page = "".join(pagelist)
        self.SetPage(page, 'page.html')
        self.Reload()

    def LoadSource(self, page):
        self.web_control.RunScript(page)

    def LoadPage(self, url):
        self.web_control.LoadURL(url)

    def Reload(self, *args, **kwargs):
        self.web_control.Reload(*args, **kwargs)

    def RunScript(self, javascript):
        self.web_control.RunScript(javascript)

    def SetPage(self, *args, **kwargs):
        self.web_control.SetPage(*args, **kwargs)
