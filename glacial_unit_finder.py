import pandas as pd
import arcpy

# Returns all rasters found in a given GDB, given there is both a top and bot layer to it
def get_raster_list(data_path : str):
    arcpy.env.workspace = data_path

    raster_top_list = []
    raster_base_list = []

    for raster in arcpy.ListRasters('*'):
        if '_top' in raster:
            raster_top_list.append(raster)
        elif '_base' in raster:
            raster_base_list.append(raster)

    raster_top_list = [item.split('_')[0] for item in raster_top_list]
    raster_base_list = [item.split('_')[0] for item in raster_base_list]

    raster_list = [item for item in raster_top_list if item in raster_base_list]

    return raster_list

# Loads CWI data from two given paths, well index and strat layers, from a given county
def load_cwi_data(cwi_path : str, st_path : str, county : int):
    cwi_wells = pd.read_csv(cwi_path, low_memory=False)
    strat_layers = pd.read_csv(st_path, low_memory=False, on_bad_lines='skip')

    cwi_wells = cwi_wells[cwi_wells['county_c'] == county]
    strat_layers = strat_layers[strat_layers['relateid'].isin(cwi_wells['relateid'])]

    wells_df = cwi_wells[['relateid', 'elevation', 'utme', 'utmn', 'data_src', 'aquifer']]
    wells_df.is_copy = False
    layers_df = strat_layers[['relateid', 'depth_top', 'depth_bot', 'color', 'hardness', 'drllr_desc', 'strat',
                              'lith_prim', 'lith_sec', 'lith_minor']]
    layers_df['geo_code'] = None
    layers_df['percentage'] = 0
    layers_df.is_copy = False

    return wells_df, layers_df

# TODO: Need to add/fix elevation and depth!
# Parses a raster for each layer found in a given dataframe, returning a dataframe containing all intersections and their percentage
def parse_raster(data_path, raster : str, wells_df : pd.DataFrame, layers_df : pd.DataFrame):
    arcpy.env.workspace = data_path

    top_raster = arcpy.Raster(f'{raster}_top')
    base_raster = arcpy.Raster(f'{raster}_base')

    top_array = arcpy.RasterToNumPyArray(top_raster, nodata_to_value=None)

    top_x_origin = top_raster.extent.XMin
    top_y_origin = top_raster.extent.YMax
    top_cell_width = top_raster.meanCellWidth
    top_cell_height = top_raster.meanCellHeight

    base_array = arcpy.RasterToNumPyArray(base_raster, nodata_to_value=None)

    base_x_origin = base_raster.extent.XMin
    base_y_origin = base_raster.extent.YMax
    base_cell_width = base_raster.meanCellWidth
    base_cell_height = base_raster.meanCellHeight

    for _, well in wells_df.dropna(subset=['utme', 'utmn', 'elevation']).iterrows():

        layers = layers_df[layers_df['relateid'] == well['relateid']]
        layers = layers.dropna(subset=['depth_top', 'depth_bot'])

        for index, layer in layers.iterrows():
            x = int(well['utme'])
            y = int(well['utmn'])

            top_x_shifted = int((x - top_x_origin) / top_cell_width)
            top_y_shifted = int((top_y_origin - y) / top_cell_height)

            base_x_shifted = int((x - base_x_origin) / base_cell_width)
            base_y_shifted = int((base_y_origin - y) / base_cell_height)

            if top_x_shifted < 0 or top_y_shifted < 0 or base_x_shifted < 0 or base_y_shifted < 0:
                print("OUT OF RASTER BOUNDS")
                continue

            gu_top = top_array[top_y_shifted, top_x_shifted]
            gu_base = base_array[base_y_shifted, base_x_shifted]

            if gu_top is None or gu_base is None or gu_top == 0 or gu_base == 0:
                continue

            elev = float(well['elevation'])
            st_top = elev - float(layer['depth_top'])
            st_bot = elev - float(layer['depth_bot'])
            st_thick = st_top - st_bot

            depth_top = min(gu_top, st_top)
            depth_bot = max(gu_base, st_bot)
            thickness = depth_top - depth_bot

            if thickness <= 0:
                continue

            percentage = thickness / st_thick

            if layers_df.loc[index, 'percentage'] < percentage:
                layers_df.loc[index, 'percentage'] = percentage
                layers_df.loc[index, 'geo_code'] = raster.upper()

def find_majority_unit(df : pd.DataFrame):
    maj_df = pd.DataFrame()

    for layer_id in df['c5st_objectid'].unique():
        layers = df[df['c5st_objectid'] == layer_id]

        maj_layer = layers[layers['percentage'] == layers['percentage'].max()]

        maj_df = pd.concat([maj_df, maj_layer[['relateid', 'glacial_unit', 'percentage','depth_top',
                                                         'depth_bot', 'elev_top', 'elev_bot']]], ignore_index=True)

    return maj_df