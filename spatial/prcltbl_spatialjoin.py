# This script will perform spatial joins between county parcel centroids and political/environmental polygon features

# Import system modules
import arcpy, os, time

start = time.time()

# Dictionary containing joining features
def shpDict(x):
    return {
        'uga': 'W:\\geodata\\political\\PSRC_region.gdb\uga',
        'juris': 'W:\\geodata\\political\\PSRC_region.gdb\psrc_region',
        'zipcode': 'W:\\geodata\\political\\zipcode.shp',
        'schooldist': 'J:\\Projects\\UrbanSim\\NEW_DIRECTORY\\GIS\\Shapefiles\\Political\\school_districts_WA.shp',
        'urbcen': 'W:\\geodata\\political\\urbcen.shp',
        'micen': 'W:\\geodata\\political\\micen.shp',
        'taz': 'W:\\geodata\\forecast\\taz2010_to_tad2010.shp',
        'faz': 'W:\\geodata\\forecast\\FAZ_2010.shp',
        'tract': 'W:\\geodata\\census\\Tract\\tract2010.shp',
        'blockgp': 'W:\\geodata\\census\\Blockgroup\\blockgrp2010.shp',
        'block': 'W:\\geodata\\census\\Block\\block2010.shp'
    }[x]

def oldFieldsDict(x):
    return {
        'uga': ['Join_Count'],
        'juris': [],
        'zipcode': ['ZCTA5CE10'],
        'schooldist': ['NAME'],
        'urbcen': ['NAME'],
        'micen': [],
        'taz': [],
        'faz': [],
        'tract': ['GEOID10'],
        'blockgp': ['GEOID10'],
        'block': ['GEOID10']
    }[x]
 
def newFieldsDict(x):
    return {
        'uga': ['IN_UGA'],
        'juris': [],
        'zipcode': ['ZIP'],
        'schooldist': ['DISTNAME'],
        'urbcen': ['URBCEN'],
        'micen': [],
        'taz': [],
        'faz': [],
        'tract': ['TRACT10'],
        'blockgp': ['BLOCKGRP10'],
        'block': ['BLOCK10']
    }[x]   

def keepFieldsDict(x):
    return{
        'uga': ['IN_UGA'],
        'juris': ['CNTYNAME', 'JURIS'],
        'zipcode': ['ZIP'],
        'schooldist': ['DISTNAME', 'DistrictID'],
        'urbcen': ['URBCEN'],
        'micen': ['MIC'],
        'taz': ['TAZ', 'TAD'],
        'faz': ['FAZ10', 'LARGE_AREA'],
        'tract': ['TRACT10'],
        'blockgp': ['BLOCKGRP10'],
        'block': ['BLOCK10']
    }[x]
    
# Environment inputs  
counties = ['Kitsap', 'Pierce', 'Snohomish', 'King'] 
shp0 = ['kitptfnl15testCopy.shp','pieptfnl15testCopy.shp', 'snoptfnl15testCopy.shp', 'kinptfnl15testCopy.shp']
joinFeaturesList = ['uga', 'juris', 'zipcode', 'schooldist', 'urbcen', 'micen', 'taz', 'faz', 'tract', 'blockgp', 'block']
target = ["overlay"+str(i) for i in range(1, len(joinFeaturesList)+1)]

rootDir = 'J:\\Projects\\UrbanSim\\NEW_DIRECTORY\\GIS\\Shapefiles\\Parcels'
homeDir = '2015_test'
shp0Dir = 'parcels_table'
outshpDir = 'spatial_overlay'

# Iterate for number of counties
for c in range(len(counties)):    
    # Set environment workspaces
    workspace = os.path.join(rootDir, counties[c], homeDir, shp0Dir)
    outWorkspace = os.path.join(rootDir, counties[c], homeDir, outshpDir, "spatial_overlay.gdb")
    arcpy.env.workspace = outWorkspace
    
    nums = range(0, len(joinFeaturesList))
    
    keepFieldsList = []
    requiredFieldsList = ["OBJECTID", "Shape"]
    
    # Iterate for number of join features
    for n in nums:
        if n == 0:
            targetFeatures = os.path.join(workspace, shp0[c])
        else:
            targetFeatures = os.path.join(outWorkspace, target[n-1])
        
        # List current target feature fields
        keepFieldsList = [f.name for f in arcpy.ListFields(targetFeatures)]
        
        outfc = os.path.join(outWorkspace, target[n])
        joinFeatures = shpDict(joinFeaturesList[n]) 
        
        # Spatial join
        arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, join_operation = "JOIN_ONE_TO_ONE", join_type = "KEEP_ALL")  
        
        # Rename fields
        oldFields = oldFieldsDict(joinFeaturesList[n])
        newFields = newFieldsDict(joinFeaturesList[n])
        
        for i in range(len(oldFields)):
            arcpy.AlterField_management(outfc, oldFields[i], newFields[i])
        
        # Extend list of 'keep' fields
        if n == 0:
            keepFieldsList.extend(requiredFieldsList)
        keepFieldsList.extend(keepFieldsDict(joinFeaturesList[n]))
        # Re-list target features fields
        fields = arcpy.ListFields(outfc)
        dropFields = [f.name for f in fields if f.name not in keepFieldsList]        
        
        # Delete fields
        arcpy.DeleteField_management(outfc, dropFields)
        
        print "Spatial joined " + counties[c] + " " + joinFeaturesList[n]

end = time.time()
print(str((end-start)/60) + " minutes")