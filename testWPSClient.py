# coding: utf-8
'''
Copyright 2010 - 2014 CRP Henri Tudor

Licenced under the EUPL, Version 1.1 or – as soon they will be approved by the
European Commission - subsequent versions of the EUPL (the "Licence");
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

http://ec.europa.eu/idabc/eupl

Unless required by applicable law or agreed to in writing, software distributed
under the Licence is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the Licence for the
specific language governing permissions and limitations under the Licence.

Created on Sep 26, 2012

@author: desousa
'''

import WPSClient
import time

iniCli = WPSClient.WPSClient()

# Basic test with literal inputs
iniCli.init(
    "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
    "test_rand_map", 
    ["delay"], 
    ["1"],
    ["rand", "region", "num"],
    ["rand", "region", "num"])

# Test with a remote GML resource
#iniCli.init(
#    "http://services.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#    "buffer", 
#    ["size","data"], 
#    ["5","http://services.iguess.tudor.lu/pywps/sampleData/testLines4326.gml"],
#    ["buffer"])

# Test with a WFS resource
# iniCli.init(
#     # Process Server address
#     "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#     # Process name
#     "buffer", 
#     # Input names
#     ["size","data"], 
#     # Input values - '&' character must be passed as '&amp;'
#     ["5","http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/Europe4326.map&amp;SERVICE=WFS&amp;VERSION=1.1.0&amp;REQUEST=getfeature&amp;TYPENAME=testLines4326&amp;srsName=EPSG:900913&amp;MAXFEATURES=10"],
#     # Output names
#     ["buffer"],
#     #Output titles
#     ["BufferedRegions"])

# Test with ultimate question
#iniCli.init(
#    # Process Server address
#    "http://services.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#    # Process name
#    "ultimatequestionprocess", 
#    # Input names
#    [], 
#    # Input values - '&' character must be passed as '&amp;'
#    [],
#    # Output names
#    ["answer"])

# Test with solar cadastre segmentation
# iniCli.init(
#     # Process Server address
#     "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#     # Process name
#     "solar_cadastre_segment", 
#     # Input names
#     ["dsm","roof_training_area","building_footprints","roof_training_area_col"], 
#     # Input values - '&' character must be passed as '&amp;'
#     ["http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WCS&amp;VERSION=1.0.0&amp;REQUEST=GetCoverage&amp;IDENTIFIER=ro_dsm_mini&amp;FORMAT=image/tiff&amp;BBOX=92217,436688,92313,436772&amp;CRS=EPSG:28992&amp;RESX=1&amp;RESY=1",
#      "http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.1.0&amp;REQUEST=getfeature&amp;TYPENAME=RO_training_areas_mini&amp;srsName=EPSG:28992",
#      "http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.1.0&amp;REQUEST=getfeature&amp;TYPENAME=RO_building_footprints_mini&amp;srsName=EPSG:28992",
#      "type"],
#     # Output names
#     ["optimum_aspect", "optimum_slope", "ro_roof_useful_intsect_gml"],
#     ["aspectMap","slopeMap","usefulRoofAreas"])

## Test with solar cadastre single process
# iniCli.init(
#     # Process Server address
#     "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#     # Process name
#     "solar_cadastre", 
#     # Input names
#     ["dsm", "roof_training_area", "roof_training_area_col", "building_footprints", "month"], 
#     # Input values - '&' character must be passed as '&amp;'
#     ["http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WCS&amp;VERSION=1.0.0&amp;REQUEST=GetCoverage&amp;IDENTIFIER=ro_dsm_mini&amp;FORMAT=image/tiff&amp;BBOX=92217,436688,92313,436772&amp;CRS=EPSG:28992&amp;RESX=1&amp;RESY=1",
#      "http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.1.0&amp;REQUEST=getfeature&amp;TYPENAME=RO_training_areas_mini&amp;srsName=EPSG:28992",
#      "type",
#      "http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/var/www/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.1.0&amp;REQUEST=getfeature&amp;TYPENAME=RO_building_footprints_mini&amp;srsName=EPSG:28992",
#      "7"
#      ],
#     # Output names
#     ["solar_irradiation"],
#     #Output titles
#     ["MySolarIrradiationMap"])

# Test with solar PV potential
# iniCli.init(
#     # Process Server address
#     "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#     # Process name
#     "solar_potential", 
#     # Input names
#     ["solar_irradiation", "potential_pv_area", "building_footprints", "econ_lifetime", "payback_price"], 
#     # Input values - '&' character must be passed as '&amp;'
#     ["http://wps.iguess.tudor.lu/pywps/sampleData/ro_solar_irradiation.tif",
#      "http://wps.iguess.tudor.lu/pywps/sampleData/ro_potential_pv_area.gml",
#      "http://wps.iguess.tudor.lu/pywps/sampleData/ro_ground_old.gml",
#      "20",
#      "0.249"
#      ],
#     # Output names
#     ["pv_potential"],
#     #Output titles
#     ["PV_potential"])

# Test with noise process
#iniCli.init(
#    # Process Server address
#    "http://services.iguess.tudor.lu/cgi-bin/pywps.cgi?", 
#    # Process name
#    "noise", 
#    # Input names
#    ["input"], 
#    # Input values - '&' character must be passed as '&amp;'
#    ["http://services.iguess.tudor.lu/pywps/sampleData/lb_dem_10m_small.tiff"],
#    # Output names
#    ["noise"],
#    #Output titles
#    ["NoisyMap"])

# Test asynchronous processing
#iniCli.init(
#    "http://10.1.15.11/cgi-bin/pywps.cgi?", 
#    "test_status", 
#    ["delay"], 
#    ["500"],
#    ["num"],
#    ["num"])

# Complete Solar Irradiation module
# iniCli.init(
#     "http://wps.iguess.tudor.lu/cgi-bin/pywps.cgi?",
#     "solar_irradiation", 
#     ['dsm','roof_training_area','octa','building_footprints','ratio','region','linke','roof_training_area_col'],
#     ['http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WCS&amp;FORMAT=image/img&amp;CRS=EPSG:28992&amp;BBOX=91979.0,436326.0,92617.0,437659.5&amp;RESX=0.5&amp;RESY=0.5&amp;VERSION=1.0.0&amp;REQUEST=getCoverage&amp;COVERAGE=ro_dsm_mini',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;CRS=EPSG:28992&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_training_areas_mini',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_octa',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;CRS=EPSG:28992&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_building_footprints_mini',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_ratio',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_clip_mini',
#      'http://services.iguess.tudor.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/RO_localOWS_test.map&amp;SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=getFeature&amp;TYPENAME=RO_linke',
#      'type'],
#     ['potential_pv_area','solar_irradiation'], 
#     ['cb_roof','cb_solar'])

url = ""
url = iniCli.sendRequest()

if(url == None):
    print "Sorry something went wrong with the request."
    print "Last message logged:\n" + iniCli.lastLogMessage

else:
    
    iniCli = None
    statCli = WPSClient.WPSClient()
    
    statCli.initFromURL(url,["pv_potential"],["PV_potential"])
#    statCli.initFromURL('http://services.iguess.tudor.lu/wpsoutputs/pywps-7f8394a2-2ff3-11e2-8730-005056a512c1.xml',
#                        ["solar_irradiation"],
#                        ["MySolarIrradiationMap"])

    while not statCli.checkStatus():
        print "Process still running"
        print str(statCli.percentCompleted) + "% completed"
        print "Status message: " + str(statCli.statusMessage)
        time.sleep(10)
        
    if(statCli.status == statCli.ERROR):
        print "There was an error. No map file was generated."
        print "Last message logged:\n" + statCli.lastLogMessage
    
    else:
        # Needed because PyWPS deletes CRS information from the outputs
        # Maybe it should be a parameter to the constructor?
        statCli.epsg = "28992"
        
        path = statCli.generateMapFile()
        print "Wrote map file to disk:\n" + path
    
    
    
    
    
    
    