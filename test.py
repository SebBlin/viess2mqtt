#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import telnetlib
import re
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
import configparser



class vclient(object):
    '''vcontrol client'''
    def __init__(self, host, port):
        print(host)
        print(port)
        self.telnet_client = telnetlib.Telnet(host, int(port))
        self.telnet_client.read_until("vctrld>")
        self.vc_tree = ET.parse(vcontrol_config_file)
        self.vito_tree = ET.parse(vito_config_file)
            

    def getValue(self, cmd):
        print("Commande : " + cmd)
        self.telnet_client.write(cmd + '\n')
        retour_cmd = self.telnet_client.read_until("vctrld>")
        retour_lignes = retour_cmd.splitlines()
        print (retour_lignes)
        print (len(retour_lignes))
        if len(retour_lignes) == 2 and retour_lignes[1]== "vctrld>":
            print ("une ligne")
            retour = retour_lignes[0]
            print("retour ", retour)
            unit = self.get_unit(cmd)
            if retour.endswith(unit):
                # on a la bonne unité en fin de ligne
                print("ok")
                val = retour[0:-len(unit)-1]
                print ("val",val)
        else:
            # retour multilignes
            toto=0
        
    def get_unit(self,cmd):
        res2 = self.vito_tree.find(".//command[@name='"+cmd+"']")
        print(res2)
        unit = res2.find('unit').text 
        print(res2.find('unit').text)
        res = self.vc_tree.find(".//unit/[abbrev='"+unit+"']")
        print (res.find('entity').text)        
        return res.find('entity').text


config_file = "vc-client.conf"
config = configparser.ConfigParser()
config.read(config_file)

HOST = config['Default']['HOST'] #192.168.0.103' # vcontrold telnet host
PORT = config['Default']['PORT'] #   '3002' # vcontrold port
vito_config_file = config['Default']['vito_config_file'] 
vcontrol_config_file = config['Default']['vcontrol_config_file'] 


vc = vclient(HOST, PORT)
vc.getValue('getTempA')
vc.getValue('getTimerM1Mo')
# vc.getValue('getDevType')

