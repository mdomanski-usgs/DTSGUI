import matplotlib as M
import logging as log

minmax_opts = dict(alpha=0.4, facecolor='#87b4f8')


class AxesBase(M.axes.Axes):
    def __init__(self, *args, **kwargs):
        M.axes.Axes.__init__(self, *args, **kwargs)
        self.canvas = self.figure.canvas
        try:
            self.profiles = self.figure.parent.profiles
            self.gridspec = self.figure.parent.grid
        except:
            self.profiles = None
            self.gridspec = None

    def set_visible(self, visible=True, index=0, orientation="columns"):
        """Orientation: columns or rows"""

        obj = getattr(self.gridspec, orientation)

        if visible: obj.show(index)
        else: obj.hide(index)
        self.gridspec.set_ratios()

        M.axes.Axes.set_visible(self,visible)
        self.figure.subplots_adjust()
        self.canvas.draw()


from cable import *
from colorbar import *
from info import *
from main import *
from time import *


from matplotlib.projections import register_projection
[register_projection(i) for i in [TimePlot, CablePlot, MainPlot, ColorBar, InfoPanel]]

