import pandas as pd
import geopandas as gpd
from geopandas import GeoSeries

geo_data_path = 'gis_data/hennepin/final_grids.gdb'

glacial_layer_names = gpd.list_layers(geo_data_path)

glacial_units = []

for _, layer_name in glacial_layer_names.iterrows():
    name = layer_name['name']
    name = name.split('_')

    if name[0] not in glacial_units:
        glacial_units.append(name[0])

with open('glacial_units.txt', 'w') as f:
    for unit in glacial_units:
        f.write(unit + ', ')