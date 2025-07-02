import csv

import pandas as pd
import arcpy
import numpy

glacial_units_path = 'glacial_units.txt'
geo_data_path = 'gis_data/hennepin.gdb'
cwi_strat_data_path = 'cwi_data/c5st.csv'
cwi_well_data_path = 'cwi_data/cwi5.csv'

save_data_path = 'output_data/c5gu.csv'

arcpy.env.workspace = geo_data_path

# Get each type of glacial unit as there are multiple layers per unit
with open(glacial_units_path, 'r') as f:
    glacial_units = f.readline().split(', ')

cwi_wells = pd.read_csv(cwi_well_data_path, low_memory=False)
strat_layers = pd.read_csv(cwi_strat_data_path, low_memory=False, on_bad_lines='skip')

cwi_wells = cwi_wells[cwi_wells['county_c'] == 27]
cwi_wells = cwi_wells.dropna(subset=['utme', 'utmn', 'elevation'])
strat_layers = strat_layers[strat_layers['relateid'].isin(cwi_wells['relateid'])]

for g_unit in glacial_units:

    top_raster = arcpy.Raster(f'{g_unit}_top')
    top_array = arcpy.RasterToNumPyArray(top_raster, nodata_to_value=None)

    top_x_origin = top_raster.extent.XMin
    top_y_origin = top_raster.extent.YMax
    top_cell_width = top_raster.meanCellWidth
    top_cell_height = top_raster.meanCellHeight

    base_raster = arcpy.Raster(f'{g_unit}_base')
    base_array = arcpy.RasterToNumPyArray(base_raster, nodata_to_value=None)

    base_x_origin = base_raster.extent.XMin
    base_y_origin = base_raster.extent.YMax
    base_cell_width = base_raster.meanCellWidth
    base_cell_height = base_raster.meanCellHeight

    gu_df = pd.DataFrame(columns=['c5st_objectid', 'relateid', 'glacial_unit', 'percentage', 'depth_top', 'depth_bot'])

    print(f'STARTING GLACIAL UNIT {g_unit}')

    for _, well in cwi_wells.iterrows():

        layers = strat_layers[strat_layers['relateid'] == well['relateid']]
        layers = layers.dropna(subset=['depth_top', 'depth_bot'])

        for _, layer in layers.iterrows():
            x = int(well['utme'])
            y = int(well['utmn'])

            top_x_shifted = int((x - top_x_origin)/top_cell_width)
            top_y_shifted = int((top_y_origin - y)/top_cell_height)

            base_x_shifted = int((x - base_x_origin)/base_cell_width)
            base_y_shifted = int((base_y_origin - y)/base_cell_height)

            # TODO: Fix this if an error arises, but unlikely
            '''if (top_x_shifted < 0 or top_y_shifted < 0 or base_x_shifted < 0 or base_y_shifted < 0 or
                top_x_shifted > top_raster.width or top_y_shifted > top_raster.height or
                base_x_shifted > base_raster.width or base_y_shifted > base_raster.height):
                print("OUT OF RASTER BOUNDS")
                continue '''

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

            percentage = thickness/st_thick

            data = {
                'c5st_objectid': layer['objectid'],
                'relateid': well['relateid'],
                'glacial_unit': g_unit,
                'percentage': percentage,
                'depth_top': depth_top,
                'depth_bot': depth_bot
            }

            gu_df.loc[len(gu_df)] = data

    print(gu_df)
    gu_df.to_csv(save_data_path, mode='a', index=False, header=None)