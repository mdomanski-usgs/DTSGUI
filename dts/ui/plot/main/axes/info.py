from dts.ui.plot.main.axes import AxesBase
import dts
import matplotlib as M


class InfoPanel(AxesBase):

    name = "InfoPanel"

    def __init__(self, *args, **kwargs):
        AxesBase.__init__(self, *args, **kwargs)
        self.set_axis_off()

        left = .12

        self.parent = self.figure.parent
        self.text(0.5,.8, "Cursor Location",size=11, ha="center")

        self.text(left,.7, "Time", size=10, weight='bold')
        self.time = self.text(left, .61, "", size=10)

        self.text(left,.5, "Distance", size=10, weight='bold')
        self.distance = self.text(left,.41, "", size=10)

        self.text(left,.3, "Temperature", size=10, weight='bold')
        self.temperature = self.text(left,.21, "", size=10)

        self.text(left,.1, "Array index", size=10, weight='bold')
        self.index = self.text(left,.01, "", size=10)
        self.update()

    def update(self):
        window = self.parent.GetTopLevelParent()

        data = self.parent.data
        x_loc = self.parent.x_loc
        t_loc = self.parent.t_loc

        time = data.get_times_list()[t_loc]
        time = dts.ui.time_format.get_datetime(time, linebreak=False)
        self.time.set_text(time)

        distance = x_loc * data.get_interval() + data.get_offset()
        self.distance.set_text('{0:.2f} m'.format(float(distance)))

        temperature = data.get_array()[t_loc,x_loc]
        self.temperature.set_text(u'{0:.2f}\u00b0C'.format(float(temperature)))

        index = '[{0:.0f},{1:.0f}]'.format(self.parent.t_loc, self.parent.x_loc)
        self.index.set_text(index)

    def set_visible(self, visible=True, index=0, orientation="columns"):
        """Orientation: columns or rows"""

        #obj = getattr(self.gridspec, orientation)

        #if visible: obj.show(index)
        #else: obj.hide(index)
        #self.gridspec.set_ratios()

        M.axes.Axes.set_visible(self,visible)
        self.figure.subplots_adjust()
        self.canvas.draw()
