import arcpy
import numpy
import pandas as pd

geo_data_path = 'gis_data/hennepin/final_grids.gdb'

arcpy.env.workspace = geo_data_path

raster = arcpy.Raster('Qf2_top')
array = arcpy.RasterToNumPyArray(raster)

x_origin = raster.extent.XMin
y_origin = raster.extent.YMax

cell_width = raster.meanCellWidth
cell_height = raster.meanCellHeight

x = 465513
y = 5006124

x_shifted = (x - x_origin)/cell_width
y_shifted = (y_origin - y)/cell_height

print(raster.hasRAT)
print(raster.functions)