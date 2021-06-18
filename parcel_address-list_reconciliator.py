# This script is for adding a field to parcels/centroids that records sent status
# The idea is to identify records that were removed from the address list csv but not the source parcel shapefile

import arcpy
import pandas as pd

address_path = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd\ComEd_address_list_2021-05-26 WITH SOCIOSSCORE.csv'
parcels = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd\Default.gdb\centroids05262021'

df = pd.read_csv(address_path)
pins = list(df.PIN.unique())

arcpy.AddField_management(parcels, "SENT", "LONG")

with arcpy.da.UpdateCursor(parcels, ["SST_PIN", "SENT"]) as cursor:
    for row in cursor:
        if int(row[0]) in pins:
            row[1] = 1
        else:
            row[1] = 0
            
        cursor.updateRow(row)