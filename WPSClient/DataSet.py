'''
Created on Aug 21, 2012

@author: Luis de Sousa [luis.desousa@tudor.lu]

Module providing tools to retrieve information from spatial datasets stored 
in the disk. This code is inspired in the UMN module of the PyWPS process [1].

[1] http://wiki.rsg.pml.ac.uk/pywps/Main_Page
'''

gdal=False
#try:
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
#except Exception,e:
#    gdal=False

DEBUG = True

class DataSet:
	"""
	Wraps spatial data sets stored in the disk. Provides methods to retrieve 
	useful information on the data set. 
	
	:param path: string with the path to the physical data set.
		
	.. attribute:: dataSet
		GDAL object wraping the spatial data set
			
	.. attribute:: dataType
		Data set type: "raster" or "vector"
			
	.. attribute:: spatialReference
		EPSG code of the coordinate system used by data set 
	"""

	dataSet=None
	dataType=None
	spatialReference=None

	def __init__(self, path):

		self.dataType = self.getDataSet(path)
		if self.dataType == None:
			return
		self.getSpatialReference()
		
		if (DEBUG):
			print "Read a data set of type " + str(self.dataType)
			print "It has the following SRS: " + str(self.getEPSG())
			print "And the following bounds: " + str(self.getBBox())
			#print "First bound: " + str(self.getBBox()[0])

	def getDataSet(self, path):
		"""
		Attempts to create a GDAL object wrapping the spatial set. Tried to
		import it first as a raster and then as vector and stores it in the
		dataSet attribute.
		
		:param path: string with the path to the physical data set 
		:returns: "raster" or "vector", None in case of error
		"""

		#logging.debug("Importing given output [%s] using gdal" % output.value)
		print "Importing given output [%s] using gdal" % path
		#If dataset is XML it will make an error like ERROR 4: `/var/www/html/wpsoutputs/vectorout-26317EUFxeb' not recognised as a supported file format.
		self.dataSet = gdal.Open(path)

		if self.dataSet:
			return "raster"

		if not self.dataSet:
			#logging.debug("Importing given output [%s] using ogr" % output.value)
			print "Importing given output [%s] using ogr" % path
			self.dataSet = ogr.Open(path)

		if self.dataSet:
			return "vector"
		else:
			print "Error importing dataset: " + path
			return None

	def getSpatialReference(self):
		"""
		Loads the Spatial Reference System defined in the data set, storing it
		in the spatialReference attribute.
		"""

		sr = osr.SpatialReference()
		if self.dataType == "raster":
			wkt = self.dataSet.GetProjection()
			res = sr.ImportFromWkt(wkt)
			if res == 0:
				self.spatialReference = sr
		elif self.dataType == "vector":
			layer = self.dataSet.GetLayer()
			ref = layer.GetSpatialRef()
			if ref:
				self.spatialReference = ref

	def getEPSG(self):
		"""
		:returns: Spatial Reference System EPSG code
		"""

		code=None
		if self.spatialReference == None:
			return None
		
		if self.spatialReference.IsProjected():
			code = self.spatialReference.GetAuthorityCode("PROJCS")
		else:
			code = self.spatialReference.GetAuthorityCode("GEOGCS")
		return code

	def getBBox(self):
		"""
		:returns: bounding box of the dataset
		"""

		if self.dataType == "raster":
			geotransform = self.dataSet.GetGeoTransform()
			#height = self.dataSet.RasterYSize
			#width = self.dataSet.RasterXSize
			return (geotransform[0],
				    geotransform[3]+geotransform[5]*self.dataSet.RasterYSize,
				    geotransform[0]+geotransform[1]*self.dataSet.RasterXSize,
				    geotransform[3])
		else:
			layer = self.dataSet.GetLayer()
			return layer.GetExtent()
		
	def getGeometryType(self):
		"""
		:returns: string with type of geometry in a vector layer: "Point", 
		"Line" or "Polygon"
		"""
		
		layer = self.dataSet.GetLayer()
		if layer <> None:
			type = ogr.GeometryTypeToName(layer.GetGeomType())
			if "Point" in type:
				return "Point"
			if "Line" in type:
				return "Line"
			if "Polygon" in type:
				return "Polygon"
		return None




