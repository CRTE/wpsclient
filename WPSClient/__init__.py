'''
Created on Aug 28, 2012

@author: Luis de Sousa [luis.desousa@tudor.lu]

This package provides tools to manage requests to a remote process server using
the Web Processing Service standard [1]. The outputs of these requests are 
fetched and published to a local map service, assuming they are of a spatial 
character when complex. The map service used is MapServer [2].
Parts of this code are inspired on the PyWPS [3] project, whose developers had
a relevant role in some of the solutions here coded.  
This package is released under the GPL-3.0 open source license [4].

[1] http://www.opengeospatial.org/standards/wps
[2] http://www.mapserver.org
[3] http://wiki.rsg.pml.ac.uk/pywps/Main_Page
[4] http://opensource.org/licenses/GPL-3.0
'''

__all__ = ["Tags","Output","DataSet","MapServerText"]

import os
import urllib2
import httplib
import logging
from ConfigParser import SafeConfigParser
from Tags import Tags
from Output import ComplexOutput
from Output import LiteralOutput
from XMLPost import XMLPost
import MapServerText as UMN
import re  # For regular expression matching

##########################################################

class WPSClient:
    """ 
    This class manages the WPS request, status checking and results 
    processing cycle. 
    
    .. attribute:: serverAddress
        Address of the WPS server where the process to invoke resides
        
    .. attribute:: processName
        Name of the process to invoke
    
    .. attribute:: inputNames
        List with the names of input arguments of the process
    
    .. attribute:: inputValues
        List with the values to pass as arguments to the process
    
    .. attribute:: outputNames
        List with the names of the process outputs. Needed to build the XML
        request
           
    .. attribute:: outputTitles
        List with the titles of outputs to use in the Map file.
    
    .. attribute:: xmlPost
        Object of the type XMLPost containing the request coded as XML sent 
        to the WPS server as an HTTP Post 
    
    .. attribute:: xmlResponse
        String with the raw XML response to the WPS request. 
            
    .. attribute:: statusURL
        URL of the remote XML file where the process updates its status and 
        writes its results after completion
    
    .. attribute:: processId
        Identifier of the remote process, part of statusURL used to identify
        the results stored locally
    
    .. attribute:: percentCompleted
        Percentage of process completion, as reported in the status XML file
        
    .. attribute:: statusMessage
        Last status message returned during asynchronous execution
        
    .. attribute:: lastLogMessage
        Last message written to the log.
            
    .. attribute:: resultsComplex
        Vector of ComplexOutput objects harbouring the complex results produced
        by the remote process
    
    .. attribute:: resultsLiteral
        Vector of LiteralOutput objects harbouring the complex results produced
        by the remote process
    
    .. attribute:: map
        Object of type MapFile used to generate the map file publishing complex
        outputs through MapServer
    
    .. attribute:: epsg
        EPSG code of the primary coordinate system used to publish complex 
        outputs
        
    .. attribute:: logFile
        Path to the log file
        
    .. attribute:: logLevel
        Level of logging
    
    .. attribute:: pathFilesGML
        Path where to store the GML files with complex outputs
    
    .. attribute:: mapServerURL
        URL of the MapServer instance to use
    
    .. attribute:: mapFilesPath
        Path where to write the map file (folder used by MapServer)
    
    .. attribute:: mapTemplate
        Path to the MapServer map template folder
    
    .. attribute:: imagePath
        Path to the MapServer image folder
    
    .. attribute:: imageURL
        URL to MapServer images folder
    
    .. attribute:: otherProjs
        String listing EPSG codes of further coordinate systems with which to
        publish the complex outputs
    """
    
    serverAddress = None
    processName = None
    inputNames = None
    inputValues = None
    outputNames = None
    outputTitles = {}
    xmlPost = None
    xmlResponse = None
    statusURL = None
    processId = None
    percentCompleted = 0
    statusMessage = None
    lastLogMessage = None
    resultsComplex = []
    resultsLiteral = []
    map  = None
    epsg = None
    
    #Configs
    logFile      = None
    logLevel     = None
    pathFilesGML = None
    mapServerURL = None
    mapFilesPath = None
    mapTemplate  = None
    imagePath    = None
    imageURL     = None
    otherProjs   = None

    RUNNING = 1
    FINISHED = 2
    ERROR = 3
    
    #Messages
    WARN_01 = "Output titles missing or incomplete, using names."
    WARN_02 = "Warning: couldn't determine the type of Complex output "
    ERR_01  = "Different number of input names and values."
    ERR_02  = "It wasn't possible to build a request with the given arguments."
    ERR_03  = "It wasn't possible to process the server address:\n"
    ERR_04  = "No status location URL found in response."
    ERR_05  = "Incomplete request -- missing URL"
    ERR_06  = "The process failed with the following message:\n"
    SUCC_01 = "The process has finished successfully.\nProcessing the results..."
    SUCC_02 = "Wrote map file to disk:\n"
    
    def __init__(self):
         
        self.loadConfigs()
        self.setupLogging()
        
    def init(self, serverAddress, processName, inputNames, inputValues, outputNames, outputTitles):
        """
        Initialises the WPSClient object with the required arguments to create
        the WPS request.
        
        :param serverAddress: string with the address of the remote WPS server
        :param processName: string with process name
        :param inputNames: list of strings with input names
        :param inputValues: list of strings with input values
        :param outputNames: list of strings with output names       
        """
        
        self.serverAddress = serverAddress
        self.processName = processName
        self.inputNames = inputNames
        self.inputValues = inputValues
        self.outputNames = outputNames       
        
        self.processOutputTitles(outputNames, outputTitles)
        
        
    def initFromURL(self, url, outputNames, outputTitles):
        """
        Initialises the WPSClient with the status URL address of a running 
        remote process. Used when a request has already been sent.
        
        :param url: string with the status URL address of a remote process      
        """
        
        self.statusURL = url
        self.processId = self.decodeId(url)
        
        self.processOutputTitles(outputNames, outputTitles)
        
        
    def loadConfigs(self):
        """ 
        Loads default attribute values from the configuration file. 
        """
        
        parser = SafeConfigParser()
        parser.read('WPSClient.cfg')
    
        self.logFile      = parser.get('Logging',   'logFile')
        self.logLevel     = parser.get('Logging',   'logLevel')
        self.pathFilesGML = parser.get('Data',      'GMLfilesPath')
        self.mapServerURL = parser.get('MapServer', 'MapServerURL')
        self.mapFilesPath = parser.get('MapServer', 'mapFilesPath')
        self.mapTemplate  = parser.get('MapServer', 'mapTemplate')
        self.imagePath    = parser.get('MapServer', 'imagePath')
        self.imageURL     = parser.get('MapServer', 'imgeURL')
        self.otherProjs   = parser.get('MapServer', 'otherProjs')
        
        
    def setupLogging(self):
        """
        Sets up the logging file.
        """
        #global logFile
        format = "[%(asctime)s] %(levelname)s: %(message)s"
        if(self.logFile == None):
            logging.basicConfig(level=self.logLevel,format=format)
        else:
            logging.basicConfig(filename=self.logFile,level=self.logLevel,format=format)
            #logFile = open(fileName, "a")
            
            
    def processOutputTitles(self, outputNames, outputTitles):
        """
        Creates the dictionary with output names and output titles.
           
        :param outputNames: array with output names
        :param outputTitles: array with output titles      
        """
        
        if(len(outputNames) <> len(outputTitles)):
            logging.warning(self.WARN_01)
            self.lastLogMessage = self.WARN_01
            for i in range(0, len(outputNames)):
                self.outputTitles[outputNames[i]] = outputNames[i]
                
        else:
            for i in range(0, len(outputNames)):
                self.outputTitles[outputNames[i]] = outputTitles[i]
        
        
    def decodeId(self, url):
        """
        Decodes the remote process identifier from the status URL.
        
        :param: string with the status URL address of a remote process
        :returns: string with the process identifier  
        """
        
        s = url.split("/")
        return s[len(s) - 1].split(".")[0] 
        
    def buildRequest(self):
        """
        Creates the XMLPost object encoding the XML request to the WPS server,
        storing it in the xmlPost attribute. 
        """
        
        if len(self.inputNames) <> len(self.inputValues):
            logging.error(self.ERR_01)
            self.lastLogMessage = self.ERR_01
            return
        
        self.xmlPost = XMLPost(self.processName)
        
        for i in range(0, len(self.inputNames)):
            if ("http://" in self.inputValues[i]): 
                self.xmlPost.addRefInput(self.inputNames[i], self.inputValues[i])
            else:
                self.xmlPost.addLiteralInput(self.inputNames[i], self.inputValues[i])
        
        for o in self.outputNames:
            self.xmlPost.addOutput(o)
            
    def sendRequest(self):
        """
        Sends the XML request encoded by the xmlPost attribute to the remote 
        WPS server through an HTTP Post. Process the response by storing the
        status URL and the process in the statusURL and processId attributes.
        
        :returns: string with the status URL, None in case of error
        """
        
        self.buildRequest()
        
        if(self.xmlPost == None):
            logging.error(self.ERR_02)
            self.lastLogMessage = self.ERR_02
            return None
        
        request = self.xmlPost.getString()
        if(request == None):
            logging.error(self.ERR_02)
            self.lastLogMessage = self.ERR_02
            return None
        
        rest = self.serverAddress.replace("http://", "")     
        split = rest.split("/")
        
        if(len(split) < 2):
            logging.error(self.ERR_03 + self.serverAddress)
            self.lastLogMessage = self.ERR_03 + self.serverAddress
            return None
        
        host = split[0]
        
        api_url = rest.replace(host, "", 1)        
        api_url = api_url.replace("?", "")
        
        logging.debug("API: " + api_url)
        logging.debug("HOST: " + host)
        logging.debug("Sending the request:\n")
        logging.debug(request + "\n")
        
        webservice = httplib.HTTP(host)
        webservice.putrequest("POST", api_url)
        webservice.putheader("Host", host)
        webservice.putheader("User-Agent","Python post")
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(request))
        webservice.endheaders()
        webservice.send(request)
        statuscode, statusmessage, header = webservice.getreply()
        self.xmlResponse = webservice.getfile().read()
        
        logging.debug("Request info:" + str(statuscode) + str(statusmessage) + str(header))
        logging.debug("Response:\n" + self.xmlResponse)
        
        try:
            self.statusURL = self.xmlResponse.split("statusLocation=\"")[1].split("\"")[0]
        except Exception, err:
            logging.error(self.ERR_04)
            self.lastLogMessage = self.ERR_04
            return None
        
        self.processId = self.decodeId(self.statusURL)
        
        return self.statusURL  

    def checkStatus(self):
        """
        Sends a request to the status URL checking the progress of the remote 
        process. If the process has finished creates the necessary Output 
        objects to fetch the results and stores them in the resultsLiteral and
        resultsComplex attributes.
        
        :returns: True if succeeded, False in case of error
        :rtype: Boolean
        """
        
        self.processError = ""
        self.processErrorCode = ""
        self.processErrorText = ""
        self.status = None                     

        if (self.statusURL == None):
            logging.error(self.ERR_05)
            self.lastLogMessage = self.ERR_05
            return False
        
        r = urllib2.urlopen(urllib2.Request(self.statusURL))
        self.xmlResponse = r.read()
        r.close()
        
        # Check if the process failed
        if (Tags.preFail in self.xmlResponse):
            self.status = self.ERROR
            self.processError = self.xmlResponse.split(Tags.preFail)[1].split(Tags.sufFail)[0]

            #                                             group1                     group2                          DOTALL makes multiline match easier
            m = re.search('<ows:Exception.+exceptionCode="([^"]+).+<ows:ExceptionText>(.+)</ows:ExceptionText>', self.processError, re.DOTALL)
            if m:
                self.processErrorCode = m.group(1)
                self.processErrorText = m.group(2).strip()
            else:
                self.processErrorCode = "Unknown"
                self.processErrorText = "Unknown"

            logging.error(self.ERR_06 + self.processErrorText)
            self.lastLogMessage = self.ERR_06 + self.processErrorText

            return True
           
        # Check if the process has finished
        if not (Tags.preSucc in self.xmlResponse):
            self.status = self.RUNNING
            logging.debug("The process hasn't finished yet.")
            if ("percentCompleted" in self.xmlResponse):
                temp = self.xmlResponse.split("percentCompleted=\"")[1]
                rest = temp.split("\">")
                self.percentCompleted = rest[0]
                self.statusMessage = rest[1].split(Tags.prStart)[0]
                logging.info(str(self.percentCompleted) + " % of the execution complete.")
            return False
        
        logging.debug(self.SUCC_01)
        self.lastLogMessage = self.SUCC_01
        
        # Process the results
        outVector = self.xmlResponse.split(Tags.preOut)
        self.status = self.FINISHED
        for o in outVector:
            if o.count(Tags.preLit) > 0:
                self.resultsLiteral.append(LiteralOutput(o))
            elif o.count(Tags.preCplx) > 0:
                self.resultsComplex.append(ComplexOutput(o, self.processId))
            # Reference outputs
            elif o.count(Tags.preRef) > 0:
                # Assumes that Complex outputs have a mimeType
                if o.count("mimeType") > 0:
                    self.resultsComplex.append(ComplexOutput(o, self.processId))
                else:
                    self.resultsLiteral.append(LiteralOutput(o))
                    
        # Save complex outputs to disk
        for c in self.resultsComplex:
            c.saveToDisk(self.pathFilesGML)
                    
        return True           
            
        
    def generateMapFile(self):
        """
        Creates the MapFile object that encodes a map file publishing the 
        complex outputs and writes it to disk.
        
        :returns: string with the path to the map file generated.
        """
        
        self.map = UMN.MapFile(self.processId)
        
        self.map.shapePath    = self.pathFilesGML
        self.map.epsgCode     = self.epsg
        self.map.mapTemplate  = self.mapTemplate
        self.map.imagePath    = self.imagePath
        self.map.imageURL     = self.imageURL
        self.map.mapServerURL = self.mapServerURL
        self.map.mapFilesPath = self.mapFilesPath
        self.map.otherProjs   = self.otherProjs
        
        for c in self.resultsComplex:
            
            if c.dataSet <> None:
                       
                if c.dataSet.dataType == "vector":
                    style = UMN.MapStyle()
                    layer = UMN.VectorLayer(
                                            c.path, 
                                            c.dataSet.getBBox(), 
                                            c.dataSet.getEPSG(), 
                                            c.name,
                                            self.outputTitles[c.name])
                    type = str(c.dataSet.getGeometryType())
                    if type <> None:
                        layer.layerType = type
                    else:
                        layer.layerType = "Polygon"
                    logging.debug("The layer type: " + str(c.dataSet.getGeometryType()))
                    layer.addStyle(style)
                    self.map.addLayer(layer)
                  
                elif c.dataSet.dataType == "raster":
                    layer = UMN.RasterLayer(
                                            c.path, 
                                            c.dataSet.getBBox(), 
                                            c.dataSet.getEPSG(), 
                                            c.name,
                                            self.outputTitles[c.name])
                    layer.setBounds(c.dataSet.getMaxValue(), c.dataSet.getMinValue())
                    self.map.addLayer(layer)
                    
                else:
                    logging.warning(self.WARN_02 + c.name)
                    self.lastLogMessage = self.WARN_02

        
        self.map.writeToDisk()
        
        logging.info(self.SUCC_02 + self.map.filePath())
        self.lastLogMessage = self.SUCC_02
            
        return self.map.filePath()
        
    def getMapFilePath(self):
        """
        Is this method really needed?
        :returns: string with the path to the generated mapfile
        """
       
        if self.map <> None:
            return self.map.filePath()
        else:
            return None     
    
    