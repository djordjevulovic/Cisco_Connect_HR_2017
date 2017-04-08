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

def CMX10_Get_Client_Location_History(mac, aftertime=0, beforetime=0):

    url_suffix = "location/v1/history/clients/%s?sortBy=lastLocatedTime:desc" % (mac)

    return CMX_GET(url_suffix)
###################################


def CMX_ClientTracler_DrawClientPath(jsonObject,im,numpoints):

    # create ImageDraw object from the Image object (provided as functional argument)
    draw = ImageDraw.Draw(im)

    # set xsize and ysize to the X/Y image sizes; use 2-tuple 'size' attribute of the Image class
    xsize=im.size[0]
    ysize=im.size[1]

    # set pointer to 'Locations'/'entries' node in the JSON output
    entries = jsonObject

    # set oldxpixel old oldypixel variables to 0
    oldxpixel = 0
    oldypixel = 0

    # browse through all entries in the JSON output
    num = 0

    for e in entries:

        # set xfeet and yfeet to the client position found in entry's MapCoordinate'/'x' and MapCoordinate'/'x'
        xfeet = e['mapCoordinate']['x']
        yfeet = e['mapCoordinate']['y']

        # set xfeetsize and yfeetsize to the image size in feet found in in entry's 'MapInfo'/'Dimension'/'width' (x) and 'MapInfo'/'Dimension'/'length' (y)
        xfeetsize = e['mapInfo']['floorDimension']['width']
        yfeetsize = e['mapInfo']['floorDimension']['length']

        # calculate X/Y position in pixels and store it xpixel/ypixel variables
        xpixel = int(xsize * xfeet/xfeetsize)
        ypixel = int(ysize * yfeet/yfeetsize)

        # using ImageDraw object draw rectangle using color 128 centered at (xpixel, ypixel) with 10 pixels in size
        if (num<numpoints):
            draw.rectangle((xpixel-5, ypixel-5, xpixel+5,ypixel+5),128,128)

        # if oldxpixel and oldypixel are both greater then 0 draw line between (xpixel,ypixel) and (oldxpixel,oldypixel) with color 128
        if (oldxpixel>0 and oldypixel>0 and num<numpoints):
            draw.line((xpixel,ypixel, oldxpixel,oldypixel), 128)

        # copy xpixel and ypixel to oldxpixel and oldypixel
        oldxpixel = xpixel
        oldypixel = ypixel

        num = num+1

def CMX_ClientTracket_Main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--mac', default = '00:00:2a:01:00:09', help="MAC Address of the client (default is 00:00:2a:01:00:09 from DevNet Sandbox")
    parser.add_argument('--numpoints', default=10, help="Number of points to show (default is 5)",type=int)
    args = parser.parse_args()

    jsonObject = CMX10_Get_Client_Location_History(args.mac)

    # use CMX_LoadFllorImage function to load floor image referenced in JOSn object
    im=CMX10_LoadImage(jsonObject[0]['mapInfo']['image']['imageName'])

    # use CMX_Demo_DrawClientPath function to draw client positions
    CMX_ClientTracler_DrawClientPath(jsonObject,im,args.numpoints)

    # display image
    im.show()

# example MAC is '00:00:2a:01:00:09'
CMX_ClientTracket_Main()
