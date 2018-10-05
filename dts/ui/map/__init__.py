import logging as log
from dts.ui.panels import NotebookChildPanel as Panel


class MapControlBase(Panel):
    """This class serves as a base for both the google maps control and static map control and holds methods common to
    each. It is designed to be subclassed and overridden appropriately."""
    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)

    def setupData(self):
        window = self.GetTopLevelParent()
        self.ch = window.status.get_current_channel()
        self.geodata = self.ch.geodata
        if not self.geodata.loaded:
            log.error("Cannot initialize "+self.__class__.__name__+": geospatial data not available.")
            self.Delete()
            self.Destroy()

    def get_marker_colors(self, temp_extents, data_series, cmap=None):
        """Prints a list of marker colors given temperature extents and a list of points in a series"""
        from dts.etc import rgb_to_hex
        window = self.GetTopLevelParent()
        # graph = window.graph_panel.get_active_main() # this is clumsy and needs to be attached to an event!!!
        if cmap is None:
            cmap = window.colors.get_colormap()
        # data = graph.data

        mn, mx = temp_extents
        log.debug("Setting marker colors for range ({0:.2f},{1:.2f})".format(float(mn), float(mx)))

        rgb = [cmap(int((i-mn)/(mx-mn)*cmap.N)) for i in data_series]
        return [rgb_to_hex(i[0:3]) for i in rgb]
