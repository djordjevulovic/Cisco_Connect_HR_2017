import requests
from requests.auth import HTTPBasicAuth
import json
from enum import Enum
###################################
# IOS XE VM in DevNet Sandbox
restconf_url_prefix = "http://ios-xe-mgmt.cisco.com:9443/api/"
restconf_username = 'root'
restconf_password = 'D_Vay!_10&'
###################################
class HTTP_Accept_Types(Enum):
    json_data = 1
    json_collection = 2

def RESTCONF_GET(url_suffix, accept_type = HTTP_Accept_Types.json_data):

    url = restconf_url_prefix + url_suffix

    # add Accept header
    if accept_type ==  HTTP_Accept_Types.json_data:
        accept_string =  'application/vnd.yang.data+json'
    elif accept_type ==  HTTP_Accept_Types.json_collection:
        accept_string = 'application/vnd.yang.collection+json'

    header = {"Accept": accept_string}

    jsonObject = {}

    try:
        response = requests.get(url, headers=header, auth=HTTPBasicAuth(restconf_username, restconf_password),verify=False)
        #print(response)

        if (response.status_code==200):
            jsonObject = response.json()

    except requests.exceptions.RequestException as e:
        print ("ERROR:" , e)

    return jsonObject

def RESTONF_GET_Interface_List():
    return RESTCONF_GET('config/native/interface/', HTTP_Accept_Types.json_data)

def RESTONF_GET_Interface_EFP_List(intf_type, intf_number):
    return RESTCONF_GET("config/native/interface/"+intf_type+"/"+intf_number+"/service", HTTP_Accept_Types.json_data)

def RESTONF_GET_EFP_Details(intf_type, intf_number, efp_number):
    return RESTCONF_GET("config/native/interface/"+intf_type+"/"+intf_number+"/service/instance/"+efp_number, HTTP_Accept_Types.json_data)

def RESTONF_GET_Interface_Config():
    return RESTCONF_GET("config/native/interface?deep", HTTP_Accept_Types.json_data)
###################################
def show_evc():

    json1 = RESTONF_GET_Interface_List()

    intf_type = "GigabitEthernet";

    print('{:10s} {:20s}  {:30s}\n'.format("EFP ID", "Interface", "Description"))
    for intf_num in json1["interface"]["GigabitEthernet"]:

        json2 = RESTONF_GET_Interface_EFP_List(intf_type, intf_num["name"])

        if (json2):
            for efp in json2["service"]["instance"]:
                json3 = RESTONF_GET_EFP_Details(intf_type, intf_num["name"], str(efp["id"]))

                if ("description" not in json3["instance"]):
                    desc = ""
                else:
                    desc = json3["instance"]["description"]

                print('{:10s} {:20s}  {:30s}'.format(str(efp["id"]), str(intf_type + intf_num["name"]), str(desc)))

def show_int_br():

    json1 = RESTONF_GET_Interface_Config()

    # print(json.dumps(json1, sort_keys=True, indent=4))

    intf_type = "GigabitEthernet"

    print ('{:30s} {:20s}  {:30s}\n'.format("Interface","IP Address", "Description"))

    for intf in json1["interface"][intf_type]:

        if ("address" not in intf["ip"]):
            ip = ""
        else:
            ip = intf["ip"]["address"]["primary"]["address"]

        if ("description" not in intf):
            desc = ""
        else:
            desc = intf["description"]

        print ('{:30s} {:20s}  {:30s}'.format(str(intf_type+intf["name"]), ip, desc))

show_evc()



