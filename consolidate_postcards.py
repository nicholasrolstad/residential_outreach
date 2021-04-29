# This script will consolidate all the postcards from a given state/utility

import arcpy
import pandas as pd
import os

state = 'IL'
resi_gdb = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\{0}\{0}_RESI.gdb'.format(state)
state_gdb = r'C:\Users\NicholasRolstad\Desktop\GDB\{}.gdb'.format(state)
utility = 'Ameren'
counties = ['Peoria', 'Champaign', 'Tazewell', 'Madison']

#!!! If GDB doesn't exist, can run following:
#arcpy.CreateFeatureDataset_management(resi_gdb,'Parcels', arcpy.SpatialReference(3435))


req_columns = ['PIN', 'NAME', 'STREET', 'CITY', 'STATE', 'ZIPCODE', 'COUNTY', 'CSV']   
postcards_dir = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\{}\{}\Postcards'.format(state, utility)
postcards = [os.path.join(postcards_dir, csv) for csv in os.listdir(postcards_dir)]

postcards_dfs = []

for csv in postcards:
    df = pd.read_csv(csv)
    df['CSV'] = csv.rsplit('\\')[-1]
    postcards_dfs.append(df)
    
all_postcards_df = pd.DataFrame(columns=req_columns) 

for df in postcards_dfs: 
    new_df = pd.DataFrame()
    new_df['PIN'] = df['PIN']
    new_df['NAME'] = df['NAME']
    new_df['STREET'] = df['STREET']
    new_df['CITY'] = df['CITY']
    new_df['STATE'] = df['STATE']
    new_df['ZIPCODE'] = df['ZIPCODE']
    new_df['COUNTY'] = df['COUNTY']
    new_df['CSV'] = df['CSV']
    new_df = new_df.astype(str) 
    all_postcards_df = all_postcards_df.append(new_df)

#counties = all_postcards_df.COUNTY.unique() #!!! This line will help you figure out what counties you need if you're unsure
pins = list(all_postcards_df.PIN.unique())
fcList = ['Parcels{}_Cleaned'.format(county) for county in counties]

arcpy.env.overwriteOutput = True
arcpy.env.workspace = resi_gdb
for fc in fcList:
    print(fc)
    arcpy.CopyFeatures_management(os.path.join(state_gdb,'ParcelCleaned',fc), os.path.join(resi_gdb, 'Parcels', fc))
    arcpy.AddField_management(os.path.join(resi_gdb, 'Parcels', fc), 'SENT', "SHORT")
    print('Copied Parcels, added SENT field.')
    with arcpy.da.UpdateCursor(os.path.join(resi_gdb, 'Parcels', fc), ["SST_PIN", "SENT"]) as cursor:
        for row in cursor:
            if row[0] in pins:
                row[1] = 1
            else:
                row[1] = 0
                
            cursor.updateRow(row)
    print('Updated SENT values')
        
        


