import osgeo.gdal as gdal
import osgeo.osr as osr
from dts.ui.map.static.spatial import Spatial
import numpy as np
import logging as log


class MapImage(Spatial):
    def __init__(self, filename=None):
        self.filename = filename
        self.image = None
        log.info("MapImage loaded")
        if self.filename is not None:
            self.__gdal__ = gdal.Open(filename)

            if self.__gdal__.RasterCount is 3:
                self.color = True

            read = lambda n: self.__gdal__.GetRasterBand(n).ReadAsArray()

            if self.color:
                r = read(1)
                g = read(2)
                b = read(3)
                self.image = np.dstack((r, g, b))

            else:
                self.image = read(1)

        Spatial.__init__(self)

        self.get_spatial_ref()

    def get_spatial_ref(self, utm_zone=18):
        self.geomatrix = self.__gdal__.GetGeoTransform()
        self.srs = osr.SpatialReference()

        proj = self.__gdal__.GetProjection()

        if proj:
            res = self.srs.ImportFromWkt(proj)
        elif self.geomatrix:
            self.srs.SetProjCS("UTM Zone {} (WGS84).".format(utm_zone))
            self.srs.SetWellKnownGeogCS("WGS84")
            log.info("Geographic information found")
            self.srs.SetUTM(utm_zone, True)
        else:
            log.error("The file has no geographic or projection information")

        self.srsLatLong = self.srs.CloneGeogCS()
