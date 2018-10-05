from dts.ui.plot.main.axes import AxesBase, minmax_opts
from dts.ui.colors import GRAY
import matplotlib as mpl


class TimePlot(AxesBase):
    name = 'TimePlot'

    def __init__(self, *args, **kwargs):
        """Axis for the **Time Range** subplot of :ref:`main-viewer`."""

        AxesBase.__init__(self, *args, **kwargs)

        self.set_xlabel(u'Temperature (\u00b0C)')
        self.xaxis.set_label_position('top')
        locator = mpl.ticker.MaxNLocator(nbins=5, prune="both")
        self.xaxis.set_major_locator(locator)

        for tick in self.yaxis.iter_ticks():
            tick[0].label1On = False

        temps = self.figure.parent.array[:, self.figure.parent.x_loc]
        time = self.figure.parent.data.get_times_list()
        t = range(len(temps))

        self.series = dict()

        plot = lambda y, color: self.plot(self.profiles['time'][y], t, color=color)
        min = self.profiles['time']['min']
        max = self.profiles['time']['max']
        from dts.ui.plot.etc import fill_between_vertical
        self.series['minmax'] = fill_between_vertical(self, min, max, t, **minmax_opts)

        self.series['mean'], = plot('mean', 'red')

        self.series['temp'], = self.plot(temps, t, color="blue")

        ax = self.twiny()
        self.series['std'] = mpl.axes.Axes.plot(ax, self.profiles['time']['std'], t, color=GRAY)[0]

        locator = mpl.ticker.NullLocator()
        ax.set_xlabel('Std dev', color=GRAY)
        locator = mpl.ticker.MaxNLocator(nbins=5, prune="lower")
        ax.xaxis.set_major_locator(locator)

        ax.xaxis.set_label_position("bottom")

        for tick in self.xaxis.iter_ticks():
            tick[0].label2On = True
            tick[0].label1On = False

        for tick in ax.xaxis.iter_ticks():
            tick[0].label2On = False
            tick[0].label1On = True

        for tl in ax.get_xticklabels():
            tl.set_color(GRAY)

        mpl.axes.Axes.set_visible(ax, self.figure.parent.c_flags['std'])
        ax.set_zorder(50)
        self.std_ax = ax

        for i, val in self.figure.parent.c_flags.items():
            self.series[i].set_visible(val)

    def set_visible(self, visible=True):
        AxesBase.set_visible(self, visible, orientation="columns", index=-1)
