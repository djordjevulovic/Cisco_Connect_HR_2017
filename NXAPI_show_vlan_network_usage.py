__author__ = 'dvulovic'

import json
import requests
from string import Template
import ast
import argparse

#######################################################################
class NXAPI_device:

    def __init__(self, ip, username, password):
        self.ip = ip
        self.url = "http://"+ip+"/ins"
        self.username = username
        self.password = password

    def NXAPI_cli_show(self, command):

        my_headers = {'content-type': 'application/json-rpc'}

        payload = [{"jsonrpc": "2.0",
                    "method": "cli",
                    "params": {"cmd": command,
                               "version": 1},
                    "id": 1}
                   ]
        try:
            response = requests.post(self.url, data=json.dumps(payload),  headers=my_headers, auth=(self.username, self.password))

        except requests.exceptions.RequestException:
            print ("ERROR: cannot send request %s to %s" % (command, self.ip))
            return None

        jsonObject = json.loads(response.text)
        return jsonObject

class NXAPI_device_DevNet_Sandbox(NXAPI_device):

    def __init__(self, num):
        if (num == 1):
            ip = "172.16.1.90"
        else:
            if (num == 2):
                ip = "172.16.1.91"
            else:
                if (num == 3):
                    ip = "172.16.1.92"
                else:
                    ip = "172.16.1.93"

        NXAPI_device.__init__(self, ip, "cisco",  "cisco")

#######################################################################

def show_vlan_usage(device_list, vlanid):

    print('{:10s} {:20s}  {:30s}\n'.format("VLAN ID", "Device IP ", "Interface"))

    for device in device_list:
        jsonObject = device.NXAPI_cli_show('show vlan id ' + vlanid)

        if jsonObject != None and "error" not in jsonObject and jsonObject["result"] != None:

#           print(json.dumps(jsonObject, sort_keys=True, indent=4))

            if ("vlanshowplist-ifidx" in jsonObject["result"]["body"]["TABLE_vlanbriefid"]["ROW_vlanbriefid"]):
                portlist = jsonObject["result"]["body"]["TABLE_vlanbriefid"]["ROW_vlanbriefid"]["vlanshowplist-ifidx"]

                ports = portlist.split(",")

                for port in ports:

                    print('{:10s} {:20s}  {:30s}'.format(str(vlanid), str(device.ip), str(port)))


parser = argparse.ArgumentParser()
parser.add_argument('--vlan', default = 1, help="VLAN ID (default 1)", type=int)
args = parser.parse_args()

show_vlan_usage([NXAPI_device_DevNet_Sandbox(1),
                 NXAPI_device_DevNet_Sandbox(2),
                 NXAPI_device_DevNet_Sandbox(3),
                 NXAPI_device_DevNet_Sandbox(4)],
                str(args.vlan))
