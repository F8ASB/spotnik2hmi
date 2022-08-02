#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################################################
# .-') _   ('-.  ) (`-.      .-') _                            .-') _      #        
#    ( OO ) )_(  OO)  ( OO ).   (  OO) )                          ( OO ) ) #
#,--./ ,--,'(,------.(_/.  \_)-./     '._ ,-.-')  .-'),-----. ,--./ ,--,'  #
#|   \ |  |\ |  .---' \  `.'  / |'--...__)|  |OO)( OO'  .-.  '|   \ |  |\  #
#|    \|  | )|  |      \     /\ '--.  .--'|  |  \/   |  | |  ||    \|  | ) #
#|  .     |/(|  '--.    \   \ |    |  |   |  |(_/\_) |  |\|  ||  .     |/  #
#|  |\    |  |  .--'   .'    \_)   |  |  ,|  |_.'  \ |  | |  ||  |\    |   #
#|  | \   |  |  `---. /  .'.  \    |  | (_|  |      `'  '-'  '|  | \   |   #
#`--'  `--'  `------''--'   '--'   `--'   `--'        `-----' `--'  `--'   #
#                                 TEAM: F0DEI,F5SWB,F8ASB      #    
############################################################################
#import echolink
import serial
import time
import os
import sys
import struct
import subprocess
import socket
import fcntl
import struct
from datetime import  *
import time
from time import time,sleep
import locale
import mmap
#partie dashboard
import urllib.request, urllib.error, urllib.parse
import ssl
url = "http://rrf.f5nlg.ovh"
#pour lecture fichier de config
import configparser, os
#pour adresse ip
import socket
#pour CPU
import io
#pour json
import json
#Pour ouverture nomenclature
import csv

#Variables:
eof=bytes([0xFF,0xFF,0xFF])
port= 0 
#Chemin fichier Json
Json="/etc/spotnik/config.json"
icao="/opt/spotnik/spotnik2hmi/datas/icao.cfg"
#routine ouverture fichier de config
svxconfig="/etc/spotnik/svxlink.cfg"
config = configparser.RawConfigParser()
config.read(svxconfig)


#Fonction pour lancement routin console

from subprocess import Popen, PIPE

#regarde la version Raspberry
def getrevision():

  # Extract board revision from cpuinfo file
    myrevision = "0000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:8]=='Revision':
                length=len(line)
                myrevision = line[11:length-1]
        f.close()
    except:
        myrevision = "0000"

    return myrevision 

def portcom(portserie,vitesse):
    global port
    port=serial.Serial(port='/dev/'+portserie,baudrate=vitesse,timeout=1, writeTimeout=1)
    print("Port serie: " +portserie+" Vitesse: "+vitesse)
    
    
def resetHMI():

    global port
    print("Reset HMI ...")
    rstcmd=b'rest' + eof
    port.write(rstcmd)
    sleep(1);

#Fonction reglage dim du nextion
def setdim(dimv):

    dimsend ='dim='+str(dimv)+eof
    port.write(dimsend)

#Fonction requete du nextion
def requete(valeur):
    requetesend = str.encode(valeur)+eof
    port.write(requetesend)

#Fonction suivre le log svxlink
def follow(thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while True:
         line = thefile.readline()
         if not line:
             time.sleep(0.1)    # Sleep briefly
             continue
         yield line

def hmiReadline():
    global port
    rcv = port.readline()
    myString = str(rcv)
    return myString

def getCPUuse():
#    return(str(os.popen("sudo top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
#)))
   CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))

    #print results
   print(("CPU Usage = " + CPU_Pct))
   return(CPU_Pct)

#Return information sur espace disque                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            disk_space=(line.split()[4])
            return(disk_space[:-1]+" %")

#Fonction de control d'extension au demarrage
def usage():
    program = os.path.basename(sys.argv[0])
    print("")   
    print("             "'\x1b[7;37;41m'"****ATTENTION****"+'\x1b[0m')
    print("")   
    print("Commande: python spotnik2hmi.py <port> <vitesse>")
    print("Ex: python spotnik2hmi.py ttyAMA0 9600")
    print("")
    sys.exit(1)

    if len(sys.argv) > 2:
        print("Ok")
    else:
        usage()

#Fonction envoyer un code DTMF au system
def dtmf(code):
    
    b = open("/tmp/dtmf_uhf","a")
    b.write(code)
    print("code DTMF: "+code)
    b.close()

#Fonction envoyer le prenom selon le call
def prenom(Searchcall):
    
    callcut = Searchcall.split (" ")
    Searchprenom = callcut[1]
    print(Searchprenom)
    lines = csv.reader(open("amat_annuaire.csv","rb"),delimiter=";")

    for indicatif,nom,prenom,adresse,ville,cp in lines:
            if indicatif==Searchprenom:
                    print(prenom)                   
#recuperation Frequence dans JSON

def get_frequency():
    global frequence
    #recherche code IMAO dans config.json
    with open(Json, 'r') as c:
        afind= json.load(c)
        frequence=afind['rx_qrg']
            
    return(frequence +" Mhz")
#recuperation indicatif dans Json       
def get_callsign():
    global indicatif
        #recherche code IMAO dans config.json
    with open(Json, 'r') as d:
        afind= json.load(d)
        call=afind['callsign']
        dept = afind['Departement']
        band = afind['band_type']           
        indicatif = "("+dept+") "+call+" "+band
    return(indicatif)        

#Fonction envoyer des commande console
def console(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    out, err = p.communicate()
    return (p.returncode, out, err)

#Fonction Wifi ECRITURE
def wifi(wifiid,wifipass):
    cfg = configparser.ConfigParser()
    cfg.read(conf)
    cfg.set('connection', 'id', wifiid)
    cfg.set('wifi', 'ssid', wifiid)
    cfg.set('wifi-security', 'psk', wifipass)
    cfg.write(open(conf,'w'))

    #lecture de donnees JSON
    with open(Json, 'r') as f:
            config = json.load(f)
    #editer la donnee
            config['wifi_ssid'] = wifiid
            config['wpa_key'] = wifipass
    #write it back to the file
    with open(Json, 'w') as f:
            json.dump(config, f)
#Fonction ecriture texte sur Nextion ex: ecrire(t0.txt,"hello word")
def ecrire(champ,texte):
    wcmd = str.encode(champ)+b'="'+str.encode(texte)+b'"'+ eof
    port.write(wcmd)

    

#Fonction appel de page
 
def page(choixnompage):
    appelpage = b'page ' + str.encode(choixnompage)+eof
    port.write(appelpage)
    infoserialpage="page " +choixnompage
    print(appelpage) 



#Fonction recherche de nom de ville selon code ICAO
def getcity():
    #lecture valeur icao dans config.json       
    with open(Json, 'r') as b:
            afind= json.load(b)
            airport =afind['airport_code']
        
    #lecture ville dans fichier icao.cfg        
    icao2city = configparser.RawConfigParser()
    config.read(icao)
    Result_city = config.get('icao2city', airport)
    #city= '"'+Result_city+'"'
    ecrire("meteo.t0.txt",Result_city) 
    print("Aeroport de: " +Result_city) 

#Fonction Meteo Lecture des donnees Metar + envoi Nextion
def get_meteo():
    #recherche code IMAO dans config.json
    with open(Json, 'r') as b:
        afind= json.load(b)
        airport =afind['airport_code']
    #Info ville Aéroport
        print("Le code ICAO est: "+airport)
        getcity()

        fichier = open("/tmp/meteo.txt", "w")
        fichier.write("[rapport]")
        fichier.close()

        result = console('/opt/spotnik/spotnik2hmi/python-metar/get_report.py '+ airport+ '>> /tmp/meteo.txt')
        print(result)
        #routine ouverture fichier de config
        config = configparser.RawConfigParser()
        config.read('/tmp/meteo.txt')

       #recuperation indicatif et frequence
        pression = config.get('rapport', 'pressure')
        temperature = config.get('rapport', 'temperature')
        rose = config.get('rapport', 'dew point')
        buletin = config.get('rapport', 'time')
        buletin = config.get('rapport', 'time')
        heure = buletin.split(':')
        heure = heure[0][-2:] + ":"+heure[1]+ ":"+heure[2][:2]
        print(heure)
        print((pression[:-2]))
        print(rose)
        print(temperature)
        ecrire("meteo.t1.txt",str(temperature))
        ecrire("meteo.t3.txt",str(heure))
        ecrire("meteo.t4.txt",str(rose))
        Pression = pression[:-2]+'hPa'
        ecrire("meteo.t2.txt",str(Pression))

def logo(Current_version):

    print('                                                 \x1b[7;30;47m'"oo" +'\x1b[0m')                                                
    print('\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m') 
    print('\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m') 
    print('\x1b[7;30;43m'+" -:::::- ::::::.  -::::-` -:::::: -:::. .:: -:: ::-   .::`     ::::-.     -::`  ::- ::::`  .::: -::`"+'\x1b[0m')
    print('\x1b[7;30;43m'+" //:---. ///.:// -//:-/// --://:- :////`:// /// ///  .//:      ---///-    ://.  //: ////- `//// ://."+'\x1b[0m')
    print('\x1b[7;30;43m'+" //:--.` ///`-// ://. ///   -//`  :////::// /// ///-///.        .///.     ://---//: /////`-//// ://."+'\x1b[0m')
    print('\x1b[7;30;43m'+" `.-:/// ///://: ://. ///   -//`  ://-///// /// ///-:///       -///:`     ://:--//: //::/://.// ://."+'\x1b[0m')
    print('\x1b[7;30;43m'+" ...-/// ///     ://:.///   -//`  ://.-//// /// ///  `///      ////-..    ://.  //: //:`///:`// ://."+'\x1b[0m')
    print('\x1b[7;30;43m'+" :::::-` ::-     `-::::-.   .::`  -::` -::: -:: ::-   ::-      :::::::    -::`  ::- ::- -::` :: -::`"+'\x1b[0m')
    print('\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m') 
    print('\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m') 
    print('                                                 \x1b[7;30;47m'"oo"+'\x1b[0m')                 
    print('\x1b[7;30;47m'"                Version :" +Current_version+"                    "           '\x1b[0m'+'\x1b[7;30;47m' + "          TEAM:"+ '\x1b[0m' +'\x1b[3;37;44m' + "/F0DEI"+ '\x1b[0m' +'\x1b[6;30;47m' + "/F5SWB"+ '\x1b[0m' + '\x1b[6;37;41m' + "/F8ASB"+ '\x1b[0m')
    print() 
    print()  

