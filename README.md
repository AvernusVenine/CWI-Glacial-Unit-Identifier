# <ins>Stratigraphy Unit Identifier
A small application utilized by the Minnesota Geological Survey [MGS](https://cse.umn.edu/mgs) that parses the County Well Index [CWI](https://www.health.state.mn.us/communities/environment/water/mwi/index.html) layers and identifies either every
code within a layer or the majority code within a layer and saves it to a .csv file.

## <ins>Creating the necessary Python environment
In order to run this application, both an active ArcGIS Pro license and installed ArcGIS Pro application is required.  A full tutorial can be found [here](https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/installing-arcpy.htm).
1) Find the ArcGIS directory (usually found under C:\Program Files)
2) Under the ArcGIS directory, locate conda.bat and set arcgispro-py3 as your environment (typically C:\Program Files\ArcGIS\Pro\bin\Python\conda\conda.bat)
   - conda activate arcgispro-py3
4) Using [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main), clone the environment above using the following command
   - conda create --clone arcgispro-py3  --name {new environment name}
5) Activate the environment using
   - conda activate {new environment name}
6) Finally, run the following command to install arcpy and be sure to install all other dependencies found in requirements.txt
   - conda install arcpy=3.5 -c esri

## <ins>How to Use
1) Select desired GeoDataBase (GDB) file under GDB Path
2) Select most up to date Main CWI .csv file under CWI5 Path
3) Select most up to date CWI Strat Layers .csv file under C5ST Path
4) Select county from which the above GDB is based off of
5) Select a desired save location
6) Select to either
- Append an existing .csv file
- Create a new file
8) Select to either
- Save every unit found within a layer
- Save only the majority unit found within a layer  

## Credits
Developed by Tate Sturm
