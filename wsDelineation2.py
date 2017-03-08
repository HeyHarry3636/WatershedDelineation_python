##------------------------------------------------------------------------------------------------------------------
##  Script Name: Watershed Delineation from Pour Points (wsDelineation2.py)
##
##  This script exports creates delineated watersheds given multiple pour points
##
##  Author: Michael Harris
##  Date: 01/13/2017
##
##------------------------------------------------------------------------------------------------------------------

#Import Modules
import arcpy, os, time

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.XYResolution = "0.00001 Meters"
arcpy.env.XYTolerance = "0.0001 Meters"

#Variables used for script run
wrkSpace = r"D:\Users\miharris\Desktop\tempGIS\workspace"
pourPoints = wrkSpace + "\\pourPointsExtract.shp"
watersheds = wrkSpace + "\\watersheds"
pourPointsCopy = arcpy.CopyFeatures_management(pourPoints, wrkSpace + "\\pourPointExtractCopy.shp")

#There is not an easy way to accept grid files as inputs, so we set up a walk to find the original DEM file
#For now, this original file must be named dem01clp
walk = arcpy.da.Walk(wrkSpace, type="GRID")
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        print filename
        if filename == "flowdir01":
            flowDir = wrkSpace + "\\" + filename
print "flowDir is " + flowDir

#Checkout Spatial Analyst extension
arcpy.AddMessage("Checking license... ")
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
    arcpy.AddMessage("Spatial Analyst license checked out... ")
else:
    arcpy.AddMessage("Spatial Analyst license needed... ")
    raise LicenseError

#Set workspace
arcpy.env.workspace = wrkSpace

#Extract each pour point into a shapefile to bue using in the watershed method
updateRows = arcpy.da.UpdateCursor(pourPointsCopy, ["FID", "Field1"])
for row in updateRows:
    print "Delineating watershed for point " + str(row[1])
    #SQL condition where it loops for every FID in the dataset
    expr = "FID = {0}".format(row[0])
    #Use select by condition to create individual shapefile for each pour point
    ws = arcpy.Select_analysis(pourPointsCopy, watersheds + "\\ws" + str(row[1]) + ".shp", expr)
    #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
    watershed = arcpy.sa.Watershed(flowDir, ws, "Field1")
    watershed.save(watersheds + "\\ws" + str(row[1]))
    #Delete point shapefile as it's no longer needed
    arcpy.Delete_management(watersheds + "\\ws" + str(row[1]) + ".shp")
    #Convert the raster of the watershed into a polygon of the watershed
    wsPoly = arcpy.RasterToPolygon_conversion(watershed, watersheds + "\\ws" + str(row[1]) + ".shp", "NO_SIMPLIFY", "VALUE")
    #Delete the raster watershed file as it's no longer needed
    arcpy.Delete_management(watersheds + "\\ws" + str(row[1]))
    #Add a drainage area field to calculate drainage area
    arcpy.AddField_management (wsPoly, "DA_sqmi", "DOUBLE")
    #Calculate drainage area
    arcpy.CalculateField_management(wsPoly, "DA_sqmi", "!SHAPE.AREA@SQUAREMILES!", "PYTHON", "")
    updateRows.updateRow(row)
del updateRows
del row


print "Done"






















