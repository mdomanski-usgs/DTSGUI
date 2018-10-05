import matplotlib as M
import logging as log


class Ratio(object):
    """
    An object that contains the screen display properties of a row or column of the main graph viewer.

    """
    def __init__(self, min=5, coef=0):
        self.min = min
        self.coef = coef
        self.hidden = False

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True

    def get_min(self):
        if self.hidden:
            return .001
        else:
            return self.min

    def get_coef(self):
        if self.hidden:
            return 0
        else:
            return self.coef


class Ratios:

    def get_param(self, attribute):
        attr = lambda obj: getattr(obj, attribute)
        col = [attr(i) for i in self.main]
        return attr(self.space)*(len(col)-1)+attr(self.before)+attr(self.after)+sum(col)

    def get_min(self):
        return self.get_param('min')

    def get_coefs(self):
        return self.get_param('coef')

    def get_ratios(self, width):
        res_width = width - self.get_min()
        # ratio = lambda obj: (obj.get_min())/float(width)

        ratio = lambda obj: (obj.get_min() + obj.get_coef()/float(self.get_coefs()) * res_width)/float(width)

        result = {
            self.key_map["space"]: ratio(self.space),
            self.key_map["before"]: ratio(self.before),
            self.key_map["after"]: 1 - ratio(self.after),
            self.key_map["main"]: [ratio(i) for i in self.main]
            }

        return result

    def hide(self, index):
        """Hides a column specified by parameter index"""
        self.main[index].hide()

    def show(self, index):
        self.main[index].show()


class Widths(Ratios):
    key_map = dict(
        space="wspace",
        before="left",
        after="right",
        main="columns"
        )
    space = Ratio(10, 0)
    before = Ratio(60, 0)
    after = Ratio(10, 0)
    main = [
        Ratio(20, 0.02),
        Ratio(70, 0.02),
        Ratio(0, 1),
        Ratio(50, .1)
        ]


class Heights(Ratios):
    key_map = dict(
        space="hspace",
        before="bottom",
        after="top",
        main="rows"
        )
    space = Ratio(10, 0)
    before = Ratio(15, .001)
    after = Ratio(40, 0)
    main = [
        Ratio(0, 1),
        Ratio(50, .2)
        ]


class MainGridSpec(M.gridspec.GridSpec):

    columns = Widths()
    rows = Heights()

    def __init__(self, parent, size=(2,4)):
        self.parent = parent

        M.gridspec.GridSpec.__init__(self, size[0], size[1])
        self.set_ratios()

        # self.parent.SetMinSize((300,300))

    def set_ratios(self):
        width, height = self.parent.canvas.GetSize().Get()
        log.debug("Dimensions: {0}, {1}".format(width, height))
        c_ratios = self.columns.get_ratios(width)
        self.set_width_ratios(c_ratios.pop('columns'))
        self.update(**c_ratios)

        r_ratios = self.rows.get_ratios(height)
        self.set_height_ratios(r_ratios.pop('rows'))
        self.update(**r_ratios)
        self.parent.figure.subplots_adjust()
        log.debug("Adjusting subplot ratios.")

    def update_inches(self):
        pass







