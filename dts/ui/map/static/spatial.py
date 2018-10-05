import osgeo.gdal as G
import osgeo.osr as osr
import numpy as N

class Spatial(object):
	"""Class to create a spatial basis for plotted images."""
	def __init__(self, xrange=None, yrange=None):
		self.xrange = xrange
		self.yrange = yrange

	def get_spatial_ref(self, filename):
		gdal_obj = G.Open(filename, G.GA_ReadOnly)		
		self.geomatrix = gdal_obj.GetGeoTransform()
		self.srs = osr.SpatialReference()
		res = self.srs.ImportFromWkt(gdal_obj.GetProjection())		
		self.srsLatLong = self.srs.CloneGeogCS()
		gdal_obj = None
		
	def set_spatial_ref(self, geo_transform, wkt):
		shape = self.shape

		driver = G.GetDriverByName("GTiff")
		from tempfile import mkstemp
		filename = mkstemp()[1]
		gdal_obj = driver.Create(filename, shape[0], shape[1], 1, G.GDT_Float32)
		gdal_obj.SetGeoTransform(geo_transform)
		gdal_obj.SetProjection(wkt)
		self.geomatrix = gdal_obj.GetGeoTransform()
		self.srs = osr.SpatialReference()
		self.srs.ImportFromWkt(gdal_obj.GetProjection())		
		self.srsLatLong = srs.CloneGeogCS()
		gdal_obj = None

	
	def m(self, px):
		'''px returns an image coordinate of the form (X, Y)'''
		geomatrix = self.geomatrix
		X = geomatrix[0] + geomatrix[1] * px[0] + geomatrix[2] * px[1]
		Y = geomatrix[3] + geomatrix[4] * px[0] + geomatrix[5] * px[1]
		return (X,Y)
		
	def px(self, map_coordinate, round=False):
		'''px returns an image coordinate of the form (X, Y)
			This only works if the image is oriented north-up.
		'''
		if self.xrange != None: xo = self.xrange[0]
		else: xo = 0
		if self.yrange != None: yo = self.yrange[0]
		else: yo = 0

		geomatrix = self.geomatrix
		x = (map_coordinate[0] - geomatrix[0])/geomatrix[1]-xo
		y = (map_coordinate[1] - geomatrix[3])/geomatrix[5]-yo
		if round: return (round(x), round(y))
		else: return (x,y)
				
	def get_pixel(self, lat, lon):
  		return self.px(self.mapc(lat, lon))
	
	def px_distance(self, point1, point2):
		'''returns spatial distance between two pixel locations in m'''
		a = self.m(point1)
		b = self.m(point2)	
		return self.distance(a,b)
	
	def distance(self, a, b):
		'''returns distance between two mapped points in m'''
		distance = N.hypot(b[0]-a[0],b[1]-a[1])
		return distance
	
	def px_to_latlon(self, point):
		'''returns the latitude and longitude for the top left corner of the given pixel of the image'''
		m = self.m(point)
		ct = osr.CoordinateTransformation(self.srs, self.srsLatLong)
		(lon, lat, height) = ct.TransformPoint(m[0],m[1])
		return lat,lon
		
	def mapc(self, lat, lon):
		'''returns the latitude and longitude in map coordinates'''
		ct = osr.CoordinateTransformation(self.srsLatLong,self.srs)
		(x, y, height) = ct.TransformPoint(lon, lat)
		return x,y
		