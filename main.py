import pandas as pd
import arcpy

glacial_units_path = 'glacial_units.txt'
geo_data_path = 'gis_data/hennepin/final_grids.gdb'
cwi_strat_data_path = 'cwi_data/c5st.csv'
cwi_well_data_path = 'cwi_data/cwi5.csv'

save_data_path = 'output_data/c5gu.csv'

arcpy.env.workspace = geo_data_path

# Get each type of glacial unit as there are multiple layers per unit
with open(glacial_units_path, 'r') as f:
    glacial_units = f.readline().split(', ')

gu_df = pd.DataFrame(columns=['c5st_seq_no', 'relateid', 'glacial_unit', 'percentage', 'depth_top', 'depth_bot'])

cwi_wells = pd.read_csv(cwi_well_data_path, low_memory=False)
strat_layers = pd.read_csv(cwi_strat_data_path, low_memory=False, on_bad_lines='skip')

cwi_wells = cwi_wells[cwi_wells['county_c'] == 27]
strat_layers = strat_layers[strat_layers['relateid'].isin(cwi_wells['relateid'])]

def layer_to_glacial_codes(well, layer):
    point_str = str(well['utme']) + ' ' + str(well['utmn'])

    for g_unit in glacial_units:
        result = arcpy.management.GetCellValue(g_unit + '_top', point_str)

        if result.getOutput(0) == 'NoData':
            continue

        gu_top = float(result.getOutput(0))
        gu_bot = float(arcpy.management.GetCellValue(g_unit + '_base', point_str).getOutput(0))

        elev = float(well['elevation'])
        st_top = elev - float(layer['depth_top'])
        st_bot = elev - float(layer['depth_bot'])
        st_thick = st_top - st_bot

        depth_top = min(gu_top, st_top)
        depth_bot = max(gu_bot, st_bot)
        intersect_thick = depth_top - depth_bot

        if intersect_thick <= 0:
            continue

        percentage = intersect_thick/st_thick

        data = {
            'c5st_seq_no': layer['c5st_seq_no'],
            'relateid': well['relateid'],
            'glacial_unit': g_unit,
            'percentage': percentage,
            'depth_top': depth_top,
            'depth_bot': depth_bot
        }

        print(data)
        gu_df.loc[len(gu_df)] = data

temp_iter = 0

for _, well in cwi_wells.iterrows():

    layers = strat_layers[strat_layers['relateid'] == well['relateid']]

    for _, layer in layers.iterrows():
        layer_to_glacial_codes(well, layer)

        temp_iter += 1

        if temp_iter > 10:
            break

    if temp_iter > 10:
        break

gu_df.to_csv(save_data_path, index=False)