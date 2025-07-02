import arcpy
import numpy as np
import pandas as pd

geo_data_path = 'gis_data/hennepin.gdb'

arcpy.env.workspace = geo_data_path

raster = arcpy.Raster('Qf2_top')
arr = arcpy.RasterToNumPyArray(raster, nodata_to_value=None)

x_origin = raster.extent.XMin
y_origin = raster.extent.YMax

cell_width = raster.meanCellWidth
cell_height = raster.meanCellHeight

x = 465513
y = 5006124

x_shifted = int((x - x_origin)/cell_width)
y_shifted = int((y_origin - y)/cell_height)

print(arcpy.management.GetCellValue('Qf2_top', str(x) + ' ' + str(y)))
print(arr[y_shifted, x_shifted])