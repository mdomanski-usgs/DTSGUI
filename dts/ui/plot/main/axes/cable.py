from dts.ui.plot.main.axes import AxesBase, minmax_opts
from dts.ui.colors import GRAY
import matplotlib as mpl


class CablePlot(AxesBase):

    """Axis for the **Space Range** subplot of :ref:`main-viewer`."""
    name = 'CablePlot'

    def __init__(self, *args, **kwargs):
        AxesBase.__init__(self, *args, **kwargs)
        self.set_autoscaley_on(True)
        self.set_ylabel(u'Temperature (\u00b0C)')

        self.series = dict()
        self.series['temp'], = self.plot(self.figure.parent.array[self.figure.parent.t_loc, :], color="blue")

        locator = mpl.ticker.MaxNLocator(nbins=5, prune="upper")
        self.yaxis.set_major_locator(locator)

        xticks = self.get_xticks()
        ticklabels = xticks + self.figure.parent.data.get_offset()
        ticklabels = ["{0:.0f}".format(label) for label in ticklabels]
        self.set_xticklabels(ticklabels)

        plot = lambda x, color: self.plot(self.profiles['space'][x], color=color)
        min = self.profiles['space']['min']
        max = self.profiles['space']['max']
        self.series['minmax'] = self.fill_between(range(len(min)), min, max, **minmax_opts)

        self.series['mean'], = plot('mean', 'red')

        ax = self.twinx()
        self.series['std'] = ax.plot(self.profiles['space']["std"], color=GRAY)[0]

        locator = mpl.ticker.MaxNLocator(nbins=5, prune="upper")
        ax.yaxis.set_major_locator(locator)
        ax.set_ylabel('Std dev', color=GRAY)
        ticklabels = ax.get_yticklabels()
        for tl in ticklabels:
            tl.set_color(GRAY)

        mpl.axes.Axes.set_visible(ax, self.figure.parent.c_flags['std'])
        ax.set_zorder(50)

        self.std_ax = ax

        for i, val in self.figure.parent.c_flags.items():
            self.series[i].set_visible(val)

    def set_visible(self, visible=True):
        AxesBase.set_visible(self, visible, orientation="rows", index=-1)
