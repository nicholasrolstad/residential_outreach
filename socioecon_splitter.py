# takes parcel datasets with a SocioEcon_Score attached, and outputs individual files for all 9 possible scores
import arcpy


counties = ['Dupage']
classes = ['HH','HM', 'MH', 'MM', 'HL', 'LH', 'LM', 'ML', 'LL']
path = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd\Default.gdb\{}_Resi' # names are County_Resi # This should be queired for service territory etc. first
arcpy.env.workspace = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd'

new_fcs = []
for county in counties:
    parcels = path.format(county)
    arcpy.MakeFeatureLayer_management(parcels, "lyr{}".format(county)) 
    for cl in classes:
        try:
            field = arcpy.AddFieldDelimiters("lyr{}".format(county), "SocioEcon_Score")
            selection = "{field} = '{val}'".format(field=field, val=cl)
            arcpy.SelectLayerByAttribute_management("lyr{}".format(county), "NEW_SELECTION", selection)
            arcpy.CopyFeatures_management("lyr{}".format(county), r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd\Default.gdb\{}_{}'.format(county,cl))
            new_fcs.append('{}_{}'.format(county,cl))
        except Exception as e:
            print(e)