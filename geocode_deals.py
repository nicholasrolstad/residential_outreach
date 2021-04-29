import arcpy
import pandas as pd
from arcgis.gis import GIS
from arcgis.geocoding import geocode, Geocoder
from arcgis.features import GeoAccessor
import keyring

state = 'IL'
SR = '3435'
date = '20210428'
resi_gdb = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\{0}\{0}_RESI.gdb'.format(state)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = resi_gdb

gis = GIS("https://www.arcgis.com", "nicholas.rolstad", keyring.get_password('esri','nicholas.rolstad'))
geocoder_url = r'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer'
w_geocoder = Geocoder(geocoder_url, gis)

csv = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\{0}\deals.csv'.format(state)
df = pd.read_csv(csv)

#arcpy.CreateFeatureDataset_management(resi_gdb,'Deals', arcpy.SpatialReference(3435))

def geocode_df(c):
    try:
        results = geocode(c['Service Address'], geocoder = w_geocoder)
    except:
        pass
    try:
        x = results[0]['location']['x']
        y= results[0]['location']['y']
        return (x,y)
    except:
        return None


def split_coord(c, coord_val):
    try:
        x,y = c['Coords']
    except:
        x,y = None, None
        
    if coord_val == 'x':
        if x:
            return str(x)
        else:
            return None
    elif coord_val == 'y':
        if y:
            return str(y)
        else:
            return None
    else:
        raise ValueError('X or Y argument only')
    
df['Coords'] = df.apply(geocode_df, axis=1)

df['X'] = df.apply(split_coord, axis=1, args=('x',))
df['Y'] = df.apply(split_coord, axis=1, args=('y',))
df.to_csv(csv, index = False, encoding='utf-8')


in_table = csv
out_feature_class = 'Deals/{0}_deals_{1}'.format(state, date)
x_coords = "X"
y_coords = "Y"

# Make the XY event layer...
arcpy.management.XYTableToPoint(in_table, 'deals.shp', x_coords, y_coords)