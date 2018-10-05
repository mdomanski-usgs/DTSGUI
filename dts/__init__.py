import matplotlib as M
M.use('WXAgg') # This must be called before any other importing of matplotlib, so we put it at the front of the script.
import logging as log
from start import Initialize
import wx
import data as data
from wx.lib.mixins.inspection import InspectionMixin
import os
import IPython # something IPython imports makes it possible to import GDAL

DEBUG = False


def get_resource(relative):
    """Gets the path to static resources, either in source directory when running from source, or as defined in the
    ``dts_app.spec`` build file."""
    try:
        return os.path.join(
            os.environ.get(
                "_MEIPASS2",
                os.path.abspath("dts", "resources")
            ),
            relative
        )
    except Exception, error:
        log.exception(error)


class Application(wx.App, InspectionMixin):
    """The main DTS GUI application."""
    def __init__(self):
        wx.App.__init__(self)
        self.data = None

    def get_data(self):
        return self.data

    def OnInit(self):
        """Initialize the Widget Inspection tool only if debug mode is on."""
        if DEBUG:
            self.Init()
        # initialize the inspection tool

        return True


class Logging:
    format = '%(levelname)s - %(pathname)s:%(lineno)d - %(message)s'

    def __init__(self):
        pass

    def set_critical(self, event=None):
        log.basicConfig(format=self.format, level=log.CRITICAL)
        print "Logging level set to critical."

    def set_error(self, event=None):
        log.basicConfig(format=self.format, level=log.ERROR)

    def set_warning(self, event=None):
        log.basicConfig(format=self.format, level=log.WARNING)

    def set_info(self, event=None):
        log.basicConfig(format=self.format, level=log.INFO)

    def set_debug(self, event=None):
        log.basicConfig(format=self.format, level=log.DEBUG)

logging = Logging()
