__author__ = 'dvulovic'

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from  PIL import Image, ImageDraw
from io import BytesIO
import argparse
###################################
# DevNet CMX Lab
cmx_url_prefix = "https://msesandbox.cisco.com:8081/api/"
cmx_username = 'learning'
cmx_password = 'learning'
###################################
def CMX_GET(url_suffix):

    url = cmx_url_prefix + url_suffix

    header = {"Accept": 'application/json'}

    # To supress warning when using DevNet CMX Sandbox
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    response = requests.get(url, headers=header, auth=HTTPBasicAuth(cmx_username, cmx_password),verify=False)

    jsonObject = response.json()

    return jsonObject


def CMX10_LoadImage(imageName):
    url = cmx_url_prefix + "config/v1/maps/imagesource/" + imageName

    # To supress warning when using DevNet CMX Sandbox
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    response = requests.get(url, auth=HTTPBasicAuth(cmx_username, cmx_password),verify=False)

    im = Image.open(BytesIO(response.content))

    return im

def CMX10_Get_Floor(campus, building, floor):

    url_suffix = "config/v1/maps/info/%s/%s/%s" % (campus, building, floor)

    return CMX_GET(url_suffix)

def CMX10_Get_All_Clients():

    url_suffix = "location/v2/clients"

    return CMX_GET(url_suffix)
###################################

def CMX_FloorVisualizer_DrawAPs(jsonObject,im):

    # create ImageDraw object from the Image object (provided as functional argument)
    draw = ImageDraw.Draw(im)

    # set xsize and ysize to the X/Y image sizes; use 2-tuple 'size' attribute of the Image class
    xsize=im.size[0]
    ysize=im.size[1]

    # set xfeetsize and yfeetsize to the image size in feet found in in entry's 'MapInfo'/'Dimension'/'width' (x) and 'MapInfo'/'Dimension'/'length' (y)
    xfeetsize = jsonObject['dimension']['width']
    yfeetsize = jsonObject['dimension']['length']

    for e in jsonObject['accessPoints']:

        # set xfeet and yfeet to the client position found in entry's MapCoordinate'/'x' and MapCoordinate'/'x'
        xfeet = e['mapCoordinates']['x']
        yfeet = e['mapCoordinates']['y']

        # calculate X/Y position in pixels and store it xpixel/ypixel variables
        xpixel = int(xsize * xfeet/xfeetsize)
        ypixel = int(ysize * yfeet/yfeetsize)

        # using ImageDraw object draw rectangle using color 128 centered at (xpixel, ypixel) with 10 pixels in size
        draw.ellipse([(xpixel-15, ypixel-15),(xpixel+15, ypixel+15)],128,128)

def CMX_FloorVisualizer_DrawClients(jsonObject,im, floorid):

    # create ImageDraw object from the Image object (provided as functional argument)
    draw = ImageDraw.Draw(im)

    # set xsize and ysize to the X/Y image sizes; use 2-tuple 'size' attribute of the Image class
    xsize=im.size[0]
    ysize=im.size[1]


    for e in jsonObject:

        if (int(e['mapInfo']['floorRefId']) == floorid):

            xfeetsize = e['mapInfo']['floorDimension']['width']
            yfeetsize = e['mapInfo']['floorDimension']['length']

            xfeet = e['mapCoordinate']['x']
            yfeet = e['mapCoordinate']['y']

            xpixel = int(xsize * xfeet/xfeetsize)
            ypixel = int(ysize * yfeet/yfeetsize)

            draw.ellipse([(xpixel-4, ypixel-4),(xpixel+4, ypixel+4)],128,128)

def CMX_FloorVisualizer_Main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--campus', default = "DevNetCampus", help="Campus (default is DevNetCampus")
    parser.add_argument('--building', default = "DevNetBuilding", help="Building (default is DevNetBuilding")
    parser.add_argument('--floor', default = "DevNetZone", help="Floor (default is DevNetZone")

    args = parser.parse_args()

    jsonObject_fl = CMX10_Get_Floor(args.campus, args.building, args.floor)

    im=CMX10_LoadImage(jsonObject_fl['image']['imageName'])

    CMX_FloorVisualizer_DrawAPs(jsonObject_fl,im)

    jsonObject_cl = CMX10_Get_All_Clients()

    CMX_FloorVisualizer_DrawClients(jsonObject_cl,im,jsonObject_fl['aesUid'])

    im.show()

CMX_FloorVisualizer_Main()
