##------------------------------------------------------------------------------------------------------------------
##  Script Name: Watershed Delineation from Pour Points (wsDelineation.py)
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
pourPoints = r"D:\Users\miharris\Desktop\tempGIS\pourPoints\pourPointsUTM.shp"
demProductPath = r"D:\Users\miharris\Desktop\tempGIS\demProducts"
threshold = 500

tableLayer = "in_memory\\tableLayer"


#There is not an easy way to accept grid files as inputs, so we set up a walk to find the original DEM file
#For now, this original file must be named dem01clp
walk = arcpy.da.Walk(demProductPath, type="GRID")
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        print filename
        if filename == "dem01clp":
            demInput = demProductPath + "\\" + filename
print "demInput is " + demInput


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

#Fill the raster to get rid of low spots in LiDAR surface, save this raster to the workspace folder
demFill = arcpy.sa.Fill(demInput)
demFill.save(wrkSpace + "\\demFill01")

#Run the flow direction process, save this raster in the workspace folder
flowDir = arcpy.sa.FlowDirection(demFill)
flowDir.save(wrkSpace + "\\flowDir01")

#Run the flow accumulation process, save this raster in the workspace folder
flowAcc = arcpy.sa.FlowAccumulation(flowDir)
flowAcc.save(wrkSpace + "\\flowAcc01")

#Create stream channels from the flow accumulation file
#Adjust threshold values if you have too many/too few channels
greaterThan = arcpy.sa.GreaterThan(flowAcc, threshold)
greaterThan.save(wrkSpace + "\\thresh" + str(threshold))

#Remove the cells of the raster that are not part of the stream channel (remove zeros, leave ones)
con = arcpy.sa.Con(greaterThan, 1)
con.save(wrkSpace + "\\strmln" + str(threshold))

#Convert the raster streamlines to vector polylines
streamlines = arcpy.sa.StreamToFeature(con, flowDir, wrkSpace + "\\streamlines" + str(threshold) + ".shp", "NO_SIMPLIFY")

#Extract the values of the flow accumulation raster to wherever the pour points are located
#This is done to see if any of the points do not line up with the streamlines
pourPointsExtract = arcpy.sa.ExtractValuesToPoints(pourPoints, flowAcc, wrkSpace + "\\pourPointsExtract.shp")

#Add the pourPointExtract.shp to the TOC and move the points that have rasterValues less than the threshold value

print "Done"






















