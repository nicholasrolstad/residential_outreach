import arcpy
import math
import pandas as pd
import os


state = 'IL'
resi_gdb = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\{0}\{0}_RESI.gdb'.format(state)
state_gdb = r'C:\Users\NicholasRolstad\Desktop\GDB\{}.gdb'.format(state)
utility = 'Ameren'
counties = ['Peoria', 'Champaign', 'Tazewell', 'Madison']
political = r"C:\USS\United States Solar Corporation\Site Selection - Documents\Data\Country\USA\Source\2020-election-results\precincts-with-results.shp"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = resi_gdb
phi = "DeleteTemp"

def create_centroids(in_polygon, out_point):
    #county = 'Wayne'
    #in_polygon = "ParcelCleaned\Parcels{}_Cleaned".format(county.title().replace(" ", ""))
    out_point = phi+"Centroid"
    Spatial_Reference   =   arcpy.Describe(in_polygon).spatialReference
    arcpy.Select_analysis(in_polygon,"Zones",'Shape_Area <> 0')
    arcpy.AddField_management("Zones","XCentroid","DOUBLE")
    arcpy.AddField_management("Zones","YCentroid","DOUBLE")
    try:
        arcpy.CalculateField_management("Zones","XCentroid","!shape.centroid.X!","PYTHON_9.3")
    except:
        pass
    try:
        arcpy.CalculateField_management("Zones","YCentroid","!shape.centroid.Y!","PYTHON_9.3")
    except:
        pass
    arcpy.MakeXYEventLayer_management("Zones", "XCentroid", "YCentroid", "Centroids", Spatial_Reference)
    arcpy.Select_analysis("Centroids",out_point)
    arcpy.Delete_management("Zones")
    arcpy.Delete_management("Centroids")
    

def delete_extra_fields(in_table, keepfields):
    fieldnames = []
    fields = arcpy.ListFields(in_table)                     
    for field in fields:
        if not field.required:                              
            fieldnames.append(field.name)
    for keepfield in keepfields:
        try:
            fieldnames.remove(keepfield)
        except:
            pass                        
    if len(fieldnames)>0:
        arcpy.DeleteField_management(in_table, fieldnames)
    

def SpatialField_Join(in_parcels, join_fc, out_field, join_field):
    #county = 'Wayne'
    #in_parcels = "ParcelCleaned\Parcels{}_Cleaned".format(county.title().replace(" ", "")) #for troubleshooting / development
    # Check if Zip Field Exists
    fields = arcpy.ListFields(in_parcels)                     
    for field in fields:
        if field.name == out_field:
            arcpy.DeleteField_management(in_parcels, [out_field])
    # Convert Parcel to Point
    create_centroids(in_parcels, phi+"Centroid")

    delete_extra_fields(phi+"Centroid", ["UID"])
    # Create Zip Copy
    arcpy.Select_analysis(join_fc, join_fc +phi)
    arcpy.AddField_management(join_fc + phi, out_field, "FLOAT")
    arcpy.CalculateField_management(join_fc + phi, out_field, "!{}!".format(join_field), "PYTHON_9.3")
    delete_extra_fields(join_fc +phi, [out_field])
    #
    # SJ Muni to Parcel
    #
    out_layer_list = []
    # Get Feature count
    feature_count = int(arcpy.GetCount_management(phi+"Centroid")[0])
    # Determine the number of splits
    split_count = int(math.ceil(feature_count/50000.0))
    start_feature = 0
    stop_feature = 50000
    for i in range(0, split_count):
        print (start_feature)
        print (stop_feature)
        arcpy.Select_analysis(phi+"Centroid", phi+"Centroid" +str(i), "OBJECTID > {0} AND OBJECTID <= {1}".format(start_feature, stop_feature))
        arcpy.SpatialJoin_analysis(phi+"Centroid"+str(i), join_fc+phi, phi+"Centroid"+str(i)+"SJ")
        out_layer_list.append(phi+"Centroid"+str(i)+"SJ")
        start_feature = stop_feature + 0
        stop_feature = stop_feature + 50000
        print ("Split #{0} SJ complete".format(i))
    # Merge output 
    arcpy.Merge_management(out_layer_list, phi+"Centroid"+"SJ")      
    # Join ZIP Field to Parcel
    arcpy.JoinField_management(in_parcels, "UID", phi+"Centroid"+"SJ", "UID", [out_field])
    # Delete Intermediate
    arcpy.Delete_management(join_fc + phi)
    arcpy.Delete_management(phi+"Centroid")
    arcpy.Delete_management(phi+"Centroid"+"SJ")
    for i in range(0, split_count):
        arcpy.Delete_management(phi+"Centroid" +str(i))
        arcpy.Delete_management(phi+"Centroid"+str(i)+"SJ")
        
#SpatialField_Join('Parcels/ParcelsChampaign_Cleaned', "election_2020", "DEM_DIFF", "pct_dem_le")
SpatialField_Join('Parcels/ParcelsChampaign_Cleaned', "Block_Group_2019", "MED_INCOME", "ALW1E001")
SpatialField_Join('Parcels/ParcelsChampaign_Cleaned', "Block_Group_2019", "TOTAL_OCC", "ALZLE001")
SpatialField_Join('Parcels/ParcelsChampaign_Cleaned', "Block_Group_2019", "OWNER_OCC", "ALZLE002")
