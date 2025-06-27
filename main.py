import pandas as pd
import geopandas as gpd
from geopandas import GeoSeries
from shapely.geometry import Point, Polygon
import pyproj

glacial_units_path = 'glacial_units.txt'
geo_data_path = 'gis_data/hennepin/final_grids.gdb'
cwi_strat_data_path = 'cwi_data/c5st.csv'
cwi_well_data_path = 'cwi_data/cwi5.csv'

save_data_path = 'output_data/c5gu.csv'

glacial_layer_names = gpd.list_layers(geo_data_path)
glacial_layers_data = {}

# Get each type of glacial unit as there are multiple layers per unit
with open(glacial_units_path, 'r') as f:
    glacial_units = f.readline().split(', ')

cwi_wells = pd.read_csv(cwi_well_data_path, low_memory=False)
strat_layers = pd.read_csv(cwi_strat_data_path, low_memory=False, on_bad_lines='skip')

cwi_wells = cwi_wells[cwi_wells['county_c'] == 27]
strat_layers = strat_layers[strat_layers['relateid'].isin(cwi_wells['relateid'])]

def save_intersect_data(g_unit : str, relate_id : str, g_series : dict):

    well_layers = strat_layers[strat_layers['relateid'] == relate_id]

    for _, layer in well_layers.iterrows():
        continue

for g_unit in glacial_units:

    g_series = {}
    g_series['top'] = gpd.read_file(geo_data_path, layer=g_unit + '_top')
    g_series['depth'] = gpd.read_file(geo_data_path, layer=g_unit + '_depth')
    g_series['thick'] = gpd.read_file(geo_data_path, layer=g_unit + '_thick')

    for _, well in cwi_wells.iterrows():
        relate_id = well['relateid']

        well_point = Point(well['utme'], well['utmn'])

        if g_series['top'].intersects(well_point):
            save_intersect_data(g_unit, relate_id, g_series)

point = Point(549276, 4871856)