#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import telnetlib
import re
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET


class vclient(object):
    '''vcontrol client'''
    def __init__(self, host, port):
        self.telnet_client = telnetlib.Telnet(host, port)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(HOST, 1883, 60)

    def publish(self, cmd):
        '''Query & Publish'''
        if cmd == 'timestamp':
            timestamp = int(time.mktime(datetime.datetime.now().timetuple())) #unix time
            self.mqtt_client.publish('/vito/' + cmd, payload=timestamp, qos=0, retain=False)	    
        else:
            self.telnet_client.read_until("vctrld>")
            self.telnet_client.write(cmd + '\n')
            waitchar = vito.getwaitchain(vito.getunit(cmd))
            if waitchar == None or waitchar == '':
                waitchar = '\n'
            print "cmd", cmd
            print "wait", waitchar
            out = self.telnet_client.read_until(waitchar)
            search = re.search(r'[0-9]*\.?[0-9]+', out)
            # return search.group(0)
            if search != None:
                pl = round(float(search.group(0)),2)
            else:
                pl=out.rstrip()
            print "cmd", cmd
            print "retour", pl
            self.mqtt_client.publish('/vito/' + cmd, payload=pl, qos=0, retain=False)

class vserverconf(object):
    '''vserverconf '''
    def __init__(self, filename1, filename2):
        self.tree = ET.parse(filename1)
        self.unit ={}
        for command in self.tree.iter('command'):
            nodeunit = command.find('unit')
            if nodeunit != None :
                self.unit[command.get('name')]= nodeunit.text

        self.tree2 = ET.parse(filename2)
        self.unitstr ={}
        for unit in self.tree2.iter('unit'):
            abbrev = ''
            entity = ''
            if unit.find('abbrev') != None:
                abbrev =  unit.find('abbrev').text
            
            if unit.find('entity') != None:
                entity = unit.find('entity').text

            if abbrev != '':
                self.unitstr[abbrev] = entity

    def getunit(self, val):
        ''' retrieve unit from value'''
        res = self.unit[val]
        return res

    def getwaitchain(self, val):
        ''' retrieve unit from value'''
        res = self.unitstr[val]
        return res


HOST = '192.168.1.103' # vcontrold telnet host
PORT = '3002' # vcontrold port

vals = ['timestamp',
        'getTempA', #	Déterminer la température extérieure en degrés C
        'getTempWWist', #	Déterminer la température de l'eau chaude en degrés C
        'getTempWWsoll', #	Déterminer la température de l'eau chaude désirée en degrés C
        'getTempKist', #	Déterminer la température de la chaudière en degrés C
        'getTempKsoll', #	Déterminer la température cible de la chaudière en degrés C
        # 'getTempVListM1', #	Déterminer la température de départ M1 en degrés C
        # 'getTempVListM2', #	Déterminer la température de départ M2 en degrés C
        # 'getTempVLsollM1', #	Déterminer la température de départ réglée M1 en degrés C
        # 'getTempVLsollM2', #	Déterminer la température de départ réglée M2 en degrés C
        # 'getTempVLsollM3', #	Déterminer la température de départ réglée M3 en degrés C
         'getTempKol', #	Déterminer la température du capteur en degrés C
         'getTempSpu', #	Déterminer la température de stockage ci-dessous en degrés C
        ## 'getTempRaumNorSollM1', #	Déterminer la température ambiante souhaitée M1 en degrés C
        # 'setTempRaumNorSollM1', #	Réglez la température de consigne de la pièce normale M1 en degrés C
        ## 'getTempRaumNorSollM2', #	Déterminer la température ambiante normale M2 en degrés C
        ## 'getTempRaumRedSollM1', #	Déterminer la température de consigne de la pièce réduit M1 en degrés C
        # 'setTempRaumRedSollM1', #	Réglez la température ambiante désirée réduite M1 en degrés C
        ## 'getTempRaumRedSollM2', #	Déterminer la température de consigne de la pièce réduit M2 en degrés C
        'getBrennerStatus', #	Déterminer l'état du brûleur
        'getBrennerStarts', #	Déterminer le nombre de démarrage du brûleur
        # 'getBrennerStunden1', #	Déterminer le niveau des heures de brûleur 1
        # 'getBrennerStunden2', #	Déterminer les heures de brûleur étape 2
        ## 'getPumpeStatusM1', #	Déterminer l'état de la pompe M1
        ## 'getPumpeStatusSp', #	Déterminer l'état de la pompe de chargement de stockage
        ## 'getPumpeStatusZirku', #	Déterminer l'état de la pompe de circulation
        ## 'getPumpeStatusSolar', #	Déterminer l'état de la pompe de circulation solaire
        # 'getPumpeStatusM2', #	Déterminer l'état de la pompe M2
        ## 'getMischerM1', #	Déterminer la position du mélangeur M1
        ## 'getMischerM2', #	Déterminer la position du mélangeur M2
        ## 'getMischerM3', #	Déterminer la position du mélangeur M3
        ## 'getSolarStatusWW', #	Déterminer l'état de la suppression de recharge
        # 'getTimerM1Mo', #	Temps de commutation lundi M1
        # 'getTimerM1Di', #	Temps de commutation mardi M1
        # 'getTimerM1Mi', #	Temps de commutation mercredi M1
        # 'getTimerM1Do', #	Temps de commutation jeudi M1
        # 'getTimerM1Fr', #	Temps de commutation vendredi M1
        # 'getTimerM1Sa', #	Temps de commutation Samedi M1
        # 'getTimerM1So', #	Temps de commutation Sunday M1
        # 'getTimerM2Mo', #	Temps de commutation lundi M2
        # 'getTimerM2Di', #	Temps de commutation mardi M2
        # 'getTimerM2Mi', #	Temps de commutation mercredi M2
        # 'getTimerM2Do', #	Temps de commutation jeudi M2
        # 'getTimerM2Fr', #	Temps de commutation vendredi M2
        # 'getTimerM2Sa', #	Temps de commutation Saturday M2
        # 'getTimerM2So', #	Temps de commutation Sunday M2
        # 'getTimerWWMo', #	Heure de commutation lundi eau chaude
        # 'getTimerWWDi', #	Heure de commutation mardi eau chaude
        # 'getTimerWWMi', #	Temps de commutation mercredi eau chaude
        # 'getTimerWWDo', #	Temps de commutation jeudi eau chaude
        # 'getTimerWWFr', #	Temps de commutation Vendredi eau chaude
        # 'getTimerWWSa', #	Heure de commutation Samedi eau chaude
        # 'getTimerWWSo', #	Temps de commutation dimanche eau chaude
        # 'getTimerZirkuMo', #	Heure de commutation lundi circu
        # 'getTimerZirkuDi', #	Temps de commutation mardi circ
        # 'getTimerZirkuMi', #	Temps de commutation mercredi cirque
        # 'getTimerZirkuDo', #	Temps de commutation jeudi cirque
        # 'getTimerZirkuFr', #	Temps de commutation vendredi cirque
        # 'getTimerZirkuSa', #	Période de commutation Saturday cirque
        # 'getTimerZirkuSo', #	Période de commutation Sunday Cirque
        ## 'getBetriebArtM1', #	Mode de fonctionnement M1
        ## 'getBetriebArtM2', #	Mode de fonctionnement M2
        ## 'getBetriebSparM1', #	Mode de fonctionnement Spar M1
        ## 'getBetriebSparM2', #	Mode de fonctionnement Spar M2
        ## 'getBetriebPartyM1', #	Mode de fonctionnement Party M1
        ## 'getBetriebPartyM2', #	Mode de fonctionnement Party M2
        # 'getSolarStunden', #	Heures de fonctionnement solaire
        # 'getSolarLeistung', #	Puissance solaire globale
        # 'getStatusFrostM1', #	Avertissement de gel M1
        # 'getStatusFrostM2', #	État d'alerte au gel M2
        # 'getStatusStoerung', #	Statut de la faute collective
         'getTempPartyM1', #	Réglez la température du mode fête M1
         'getTempPartyM2', #	Réglez la température du mode fête M2
         'getSystemTime', #	Déterminer l'heure du système
        # 'setSystemTime', #	Définir l'heure du système
        # 'setTempWWsoll', #	Réglez la température d'eau chaude désirée en degrés C
        # 'setTempPartyM1', #	Réglez la température cible de l'eau chaude Partie M1 en degrés C
        # 'setTempPartyM2', #	Réglez la température de consigne d'eau chaude Party M2 en degrés C
        # 'setBetriebArtM1', #	Réglez le mode de fonctionnement M1
        # 'setBetriebSparM1', #	Réglez le mode de fonctionnement Spar M1
        # 'setBetriebPartyM1', #	Réglez le mode de fonctionnement Party M1
        # 'setBetriebPartyM2', #	Réglez le mode opératoire Party M2
        # 'setPumpeStatusZirku', #	Définir l'état de la pompe de circulation
        # 'setTimerM1Mo', #	Temps de commutation lundi M1
        # 'setTimerM1Di', #	Temps de commutation mardi M1
        # 'setTimerM1Mi', #	Temps de commutation mercredi M1
        # 'setTimerM1Do', #	Temps de commutation jeudi M1
        # 'setTimerM1Fr', #	Temps de commutation vendredi M1
        # 'setTimerM1Sa', #	Temps de commutation Samedi M1
        # 'setTimerM1So', #	Temps de commutation Sunday M1
        # 'setTimerM2Mo', #	Temps de commutation lundi M2
        # 'setTimerM2Di', #	Temps de commutation mardi M2
        # 'setTimerM2Mi', #	Temps de commutation mercredi M2
        # 'setTimerM2Do', #	Temps de commutation jeudi M2
        # 'setTimerM2Fr', #	Temps de commutation vendredi M2
        # 'setTimerM2Sa', #	Temps de commutation Saturday M2
        # 'setTimerM2So', #	Temps de commutation Sunday M2
        # 'setTimerWWMo', #	Heure de commutation lundi eau chaude
        # 'setTimerWWDi', #	Heure de commutation mardi eau chaude
        # 'setTimerWWMi', #	Temps de commutation mercredi eau chaude
        # 'setTimerWWDo', #	Temps de commutation jeudi eau chaude
        # 'setTimerWWFr', #	Temps de commutation Vendredi eau chaude
        # 'setTimerWWSa', #	Heure de commutation Samedi eau chaude
        # 'setTimerWWSo', #	Temps de commutation dimanche eau chaude
        # 'setTimerZirkuMo', #	Heure de commutation lundi circu
        # 'setTimerZirkuDi', #	Temps de commutation mardi circ
        # 'setTimerZirkuMi', #	Temps de commutation mercredi cirque
        # 'setTimerZirkuDo', #	Temps de commutation jeudi cirque
        # 'setTimerZirkuFr', #	Temps de commutation vendredi cirque
        # 'setTimerZirkuSa', #	Période de commutation Saturday cirque
        # 'setTimerZirkuSo', #	Période de commutation Sunday Cirque
        # 'getError0', #	Déterminer l'entrée de l'historique des erreurs 1
        # 'getError1', #	Déterminer l'entrée de l'historique des erreurs 2
        # 'getError2', #	Déterminer l'entrée de l'historique des erreurs 3
        # 'getError3', #	Déterminer l'entrée de l'historique des erreurs 4
        # 'getError4', #	Déterminer l'entrée de l'historique des erreurs 5
        # 'getError5', #	Déterminer l'entrée de l'historique des erreurs 6
        # 'getError6', #	Déterminer l'entrée de l'historique des erreurs 7
        # 'getError7', #	Déterminer l'entrée de l'historique des erreurs 8
        # 'getError8', #	Déterminer l'entrée de l'historique des erreurs 9
        # 'getError9', #	Déterminer l'entrée de l'historique des erreurs 10
        # 'getNeigungM1', #	Déterminer la caractéristique de chauffage de la pente M1
        # 'getNeigungM2', #	Déterminer la caractéristique de chauffage de la pente M2
        # 'getNiveauM1', #	Déterminer la caractéristique de chauffage de niveau M1
        # 'getNiveauM2', #	Déterminer la courbe de chauffage de niveau M2
        # 'setNeigungM1', #	Régler l'inclinaison caractéristique de chauffage M1
        # 'setNeigungM2', #	Réglez l'inclinaison caractéristique de chauffage M2
        # 'setNiveauM1', #	Définir la caractéristique de chauffage de niveau M1
        # 'setNiveauM2', #	Définir la caractéristique de chauffage de niveau M2
        ## 'getDevType' #	Déterminer le type d'appareil de l'usine	
         ]

vc = vclient(HOST, PORT)
vito = vserverconf('/home/pi/viess2mqtt/vito.xml','/home/pi/viess2mqtt/vcontrold.xml')


for v in vals:
    vc.publish(v)
