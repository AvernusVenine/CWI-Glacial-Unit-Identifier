import pandas as pd

cwi_strat_data_path = 'cwi_data/c5st.csv'
cwi_well_data_path = 'cwi_data/cwi5.csv'
glacial_data_path = 'output_data/c5gu_hennepin_updated.csv'

majority_glacial_data_path = 'output_data/hennepin_glacial_majority.csv'

cwi_layers = pd.read_csv(cwi_strat_data_path, low_memory=False, on_bad_lines='skip')
glacial_units = pd.read_csv(glacial_data_path, low_memory=False)

majority_glacial = pd.DataFrame()

for layer_id in glacial_units['c5st_objectid'].unique():
    layers = glacial_units[glacial_units['c5st_objectid'] == layer_id]

    maj_layer = layers[layers['percentage'] == layers['percentage'].max()]
    majority_glacial = pd.concat([majority_glacial, maj_layer[['relateid', 'glacial_unit', 'percentage',
                                        'depth_top', 'depth_bot', 'elev_top', 'elev_bot']]], ignore_index = True)

majority_glacial.sort_values(by=['relateid', 'depth_top'])

majority_glacial.to_csv(majority_glacial_data_path, index=False)
    
