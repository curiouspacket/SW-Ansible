#!/usr/bin/env python3


'''
Custom dynamic inventory script for Ansible and Solar Winds, in Python.

Original code:
(c) 2017, Chris Babcock (chris@bluegreenit.com)

Modifed by curiouspacket 2020
'''
import argparse
import configparser
import requests
import re
import csv
import getpass

try:
    import json
except ImportError:
    import simplejson as json


config_file = 'swinds.ini'




# Orion Server IP or DNS/hostname
server = '10.210.240.95'
# Orion Username
user = input('what is your username: \n')
# Orion Password
print('What is your Password: ')
password = getpass.getpass()


# Field for groups
groupField = 'Location'
# Field for host in groups
hostField = 'IPAddress'
hostID = 'SysName'


#Query to Solarwinds
payload="query=SELECT NodeID, SysName, IPAddress, Vendor, Location FROM Orion.Nodes WHERE Vendor='Cisco'"



use_groups = False
parentField = 'ParentGroupName'
childField = 'ChildGroupName'

#payload = "query=SELECT+" + hostField + "+," + groupField + "+FROM+Orion.Nodes"
url = "https://"+server+":17778/SolarWinds/InformationService/v3/Json/Query"
req = requests.get(url, params=payload, verify=False, auth=(user, password))

jsonget = req.json()


class SwInventory(object):

    # CLI arguments
    def read_cli(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        self.options = parser.parse_args()

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.get_list()
            if use_groups:
                self.groups = self.get_groups()
                self.add_groups_to_hosts(self.groups)
        else:
            self.inventory = self.empty_inventory()

        #print(json.dumps(self.inventory, indent=2))
    def get_list(self):
        hostsData = jsonget
        dumped = eval(json.dumps(jsonget))
        #print(dumped)
        # Inject data below to speed up script
        final_dict = {'Devices': {'hostvars': {}}}
        hosts_dict = { }
        # Loop hosts in groups and remove special chars from group names
        for m in dumped['results']:
            # Allow Upper/lower letters and numbers. Replace everything else with underscore
            m[groupField] = self.clean_inventory_item(m[groupField])
            if m[groupField] in final_dict:
                #If Group(Location) is present add Hosts and IPs
                final_dict[m[groupField]]['hosts'].update({m[hostField] : m[hostID]})
            
               
            else:
                #If Group(Location) is not present create it and add firest Host and IP
                final_dict[m[groupField]] = {'hosts': {m[hostField] : m[hostID]}}
               
            
        #with open('test.csv', 'w') as f:
         # for key in final_dict.keys():
          #   f.write("%s,%s\n"%(key,final_dict[key]))
        #Saves Hosts Dictionary to File
        with open('test-1.txt', 'w') as f:
          for key in final_dict.keys():
             f.write("%s,%s\n"%(key,final_dict[key]))
        #print(final_dict)
          
        return final_dict

    

    def add_groups_to_hosts (self, groups):
        self.inventory.update(groups)

    @staticmethod
    def clean_inventory_item(item):
        item = re.sub('[^A-Za-z0-9]+', '_', item)
        return item

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()

# Get the inventory.
SwInventory()
