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

    def NXAPI_cli_config(self, command_list):

        # jsonrpc_template = Template("{'jsonrpc': '2.0', 'method': '$method', 'params': ['$params', 1], 'id': '$jrpc_id'}")
        jsonrpc_template = Template(
            "{'jsonrpc': '2.0', 'method': '$method', 'params': {'cmd': '$cmd', 'version': 1}, 'id': '$jrpc_id'}")

        batch_cmd = "[" + jsonrpc_template.substitute(cmd="conf t", jrpc_id=1, method='cli')

        id_counter = 2

        for command in command_list:

            batch_cmd = batch_cmd + "," + jsonrpc_template.substitute(cmd=command, jrpc_id=id_counter, method='cli')
            id_counter += 1

        batch_cmd = batch_cmd + "," + jsonrpc_template.substitute(cmd="exit", jrpc_id=id_counter, method='cli') + "]"

        my_headers = {'content-type': 'application/json-rpc'}

        try:
            response = requests.post(self.url, data=json.dumps(ast.literal_eval(batch_cmd)), headers=my_headers, auth=(self.username, self.password))
        except requests.exceptions.RequestException:
            print ("ERROR: cannot send config request to %s" % (self.ip))
            return None

        return response

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

##############################################
def create_vlan_on_network(device_list, vlanid, vlanname):

    print('Creating VLAN {} ({})'.format(vlanid, vlanname))

    for device in device_list:

        response = device.NXAPI_cli_config(['vlan ' +vlanid,'name ' + vlanname])

        if response == None or response.status_code != 200:
            print("Device " + device.ip + " FAILED")
        else:
            print("Device " + device.ip + " OK")

parser = argparse.ArgumentParser()
parser.add_argument('vlan', help="VLAN ID", type=int)
parser.add_argument('name', help="Name", type=str)
args = parser.parse_args()

create_vlan_on_network([NXAPI_device_DevNet_Sandbox(1),
                 NXAPI_device_DevNet_Sandbox(2),
                 NXAPI_device_DevNet_Sandbox(3),
                 NXAPI_device_DevNet_Sandbox(4)],
                 str(args.vlan), args.name)
