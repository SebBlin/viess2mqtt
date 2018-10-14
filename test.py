#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import telnetlib
import re
# import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
import configparser
from wsgiref.simple_server import make_server


class vclient(object):
    '''vcontrol client'''
    def __init__(self, host, port):
        self.telnet_client = telnetlib.Telnet(host, int(port))
        self.telnet_client.read_until("vctrld>")
        self.vc_tree = ET.parse(vcontrol_config_file)
        self.vito_tree = ET.parse(vito_config_file)
            

    def getValue(self, cmd):
        self.telnet_client.write(cmd + '\n')
        retour_cmd = self.telnet_client.read_until("vctrld>")
        retour_lignes = retour_cmd.splitlines()
        if len(retour_lignes) == 2 and retour_lignes[1]== "vctrld>":
            retour = retour_lignes[0]
            unit = self.get_unit(cmd)
            if retour.endswith(unit):
                # on a la bonne unité en fin de ligne
                val = retour[0:-len(unit)-1]
                return val
        else:
            # retour multilignes
            toto=0
        
    def get_unit(self,cmd):
        res2 = self.vito_tree.find(".//command[@name='"+cmd+"']")
        unit = res2.find('unit').text 
        res = self.vc_tree.find(".//unit/[abbrev='"+unit+"']")
        return res.find('entity').text

def check_uri(uri):
    if uri[0]=='/':
        uri = uri[1:]
        print (uri)
    res2 = vc.vito_tree.find(".//command[@name='"+uri+"']")
    if res2 :
        return True
    else:
        return False


def vcserver(environ, start_response):
    status = '200 OK'  # HTTP Status
    headers = [('Content-type', 'text/plain; charset=utf-8')]  # HTTP Headers
    start_response(status, headers)
    uri = environ['PATH_INFO']
    if check_uri(uri):
        return vc.getValue('getTempA')
    else:
        return [b"Unknown command" + uri]


config_file = "vc-client.conf"
config = configparser.ConfigParser()
config.read(config_file)

HOST = config['Default']['HOST'] #192.168.0.103' # vcontrold telnet host
PORT = config['Default']['PORT'] #   '3002' # vcontrold port
server_port = config['Server']['PORT'] #   '3003' # vcontrold port of Web Server
vito_config_file = config['Default']['vito_config_file'] 
vcontrol_config_file = config['Default']['vcontrol_config_file'] 


vc = vclient(HOST, PORT)

httpd = make_server('', 8000, vcserver)
print("Serving on port 8000...")
# Serve until process is killed
httpd.serve_forever()

# temp = vc.getValue('getTempA')
# print("res " + temp )

# vc.getValue('getTimerM1Mo')
# # vc.getValue('getDevType')

