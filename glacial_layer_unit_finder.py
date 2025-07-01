import pandas as pd
import arcpy

geo_data_path = 'gis_data/hennepin/final_grids.gdb'

arcpy.env.workspace = geo_data_path

rasters = arcpy.ListRasters('*')

for raster in rasters:
    print(raster)