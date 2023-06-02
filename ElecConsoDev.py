#!/usr/bin/python
# -*- coding: utf-8 -*-
 
#=========================================================================
#              elec.py
#-------------------------------------------------------------------------
# Modifications done by Bruno Faucon - 2023, April
# version 0.4 2023-04-07#
# Read the solar consumption directly on the SMA SunnyBoy
# Using the code SMA-SunnyBoy found there: https://github.com/Dymerz/SMA-SunnyBoy
#-------------------------------------------------------------------------
# This script read the total energy produciton on sunnyboy 
# compare the old values to the new one and save the values in a MySQL database
#
# tested with python 3 on Raspberry pi distribution: Raspbian GNU/Linux 11 (bullseye) 
#-------------------------------------------------------------------------

#===================================================================
 
#----------------------------------------------------------#
#             package importation                          #
#----------------------------------------------------------#
import os
import sys
import time
import datetime
import  urllib.request, json
import MySQLdb   # MySQLdb must be installed by yourself
from threading import Timer
from sma_sunnyboy import *
from SendMail import *

#import sqlite3s
 
#-----------------------------------------------------------------#
#  constants : use your own values / utilisez vos propres valeurs #
#-----------------------------------------------------------------#
PATH_THERM = "/home/pi/NewConso/" #path to this script
PATH_LOG = "/home/pi/NewConso/test/" #path to this script

DB_SERVER ='192.168.2.10'  # MySQL : IP server (localhost if mySQL is on the same machine)
DB_USER='conso'     # MySQL : user
DB_PWD='WXH.Yrb24RdU'            # MySQL : password
DB_BASE='NewConso'     # MySQL : database name
#DB_BASE='consumption'     # MySQL : database name
DB_PORT=3307

 
# vous pouvez ajouter ou retirer des sondes en modifiant les lignes ci dessous
# ainsi que la derniere ligne de ce script : querydb(....
counter1 = "192.168.2.95" #SMA Gauche
counter2 = "192.168.2.21" #SMA Droite
counter3 = "http://192.168.2.22/api/v1/data" #Homewizard P1
counter4 = "http://192.168.2.23/api/v1/data" #HomeWizard SDM230 Chauffe eau
counter5 = "http://192.168.2.24/api/v1/data" #HomeWizard Socket
counter6 = "http://192.168.2.25/api/v1/data" #HomeWizard SDM230 Jacuzzi
old1 = PATH_LOG + "oldSMAG1"
old2 = PATH_LOG + "oldSMAD1"
old3 = PATH_LOG + "oldTPI1"
old4 = PATH_LOG + "oldTPI2"
old5 = PATH_LOG + "oldTPE1"
old6 = PATH_LOG + "oldTPE2"
old7 = PATH_LOG + "oldTPI3"
old8 = PATH_LOG + "oldTPI4" 
old9 = PATH_LOG + "oldSocket1"
old10 = PATH_LOG + "oldJacuzzi"
#----------------------------------------------------------#
#             Variables                                    #
#----------------------------------------------------------#
debug = False

#----------------------------------------------------------#
#     definition : database query                          #
#----------------------------------------------------------#
def query_db(sql):
    db = MySQLdb.connect(DB_SERVER, DB_USER, DB_PWD, DB_BASE, DB_PORT)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close() 

#----------------------------------------------------------#
#     definition : new query for sonde                     #
#----------------------------------------------------------#
def read_SMA(counter):
    try:
        client = WebConnect(counter, Right.USER, "Stego123?", port=443, use_ssl=True)
        client.auth()
        pow_current = client.get_value(Key.power_current)
        power_total = client.get_value(Key.power_total)
        client.logout()
        if (str(pow_current) ==  'None'):
           pow_current = '0'
#        else:
#           log ("SMA "+counter, 'info')
    except:
        log('SMA Sunnyboy not reachable please take action', 'error')
        pow_current = '0'
        power_total = '0'
    finally:
        return pow_current, power_total

#----------------------------------------------------------#
#     definition : debug                                   #
#----------------------------------------------------------#
def log(message, level):
    message = str(message)
    if level == 'info':
        if debug == 'info':
            print("Info "+ message)
    elif level== 'warning':
        if debug != 'error':
            print("Warning " + message)
    else:
        print("Error " + message)  
        send_mail('rpi@one2care.be', 'bruno.faucon@one2care.be', 'Alerte Raspberry', message)
        
#----------------------------------------------------------#
#     definition : new query for sonde                     #
#----------------------------------------------------------#
def read_homewizard_P1(counter):
    try:
        response = urllib.request.urlopen(counter)
        data = json.loads(response.read())
        #log (response)
        log (data, 'info')
        active_power_w = int((data['active_power_w']))
        total_power_import_t1_kwh = int((1000*data['total_power_import_t1_kwh']))
        total_power_import_t2_kwh = int((1000*data['total_power_import_t2_kwh']))
        total_power_export_t1_kwh = int((1000*data['total_power_export_t1_kwh']))
        total_power_export_t2_kwh = int((1000*data['total_power_export_t2_kwh']))
        #log ('Status')
        #log ("Active power: " + str(active_power_w))
        #log ("Total power In T1: " + str(int(total_power_import_t1_kwh)))
        #log ("Total power In T2: " + str(int(total_power_import_t2_kwh)))
        #log ("Total power Out T1: " + str(int(total_power_export_t1_kwh)))
        #log ("Total power Out T2: " + str(int(total_power_export_t2_kwh)))
    except:
        log('Homewizard P1 not reachable please take action','error')
        active_power_w = 0
        total_power_import_t1_kwh = 0
        total_power_import_t2_kwh = 0
        total_power_export_t1_kwh = 0
        total_power_export_t2_kwh = 0
    finally:
        return active_power_w, total_power_import_t1_kwh, total_power_import_t2_kwh, total_power_export_t1_kwh, total_power_export_t2_kwh

#----------------------------------------------------------#
#     definition : new query for HomeWizard SDM230         #
#----------------------------------------------------------#
def read_homewizard_SDM230(counter):
    try:
        response = urllib.request.urlopen(counter)
        data = json.loads(response.read())
        #log (response)
        log (data, 'info')
        active_power_w = int((data['active_power_w']))
        total_power_import_wh = int(1000*(data['total_power_import_kwh']))
        #log ('Status')
        #log ("Active power: " + str(active_power_w))
        #log ("Total power In T1: " + str(int(total_power_import_wh)))
    except:
        log('Homewizard SDM230 not reachable please take action','error')
        active_power_w = 0
        total_power_import_wh = 0
    finally:
        return active_power_w, total_power_import_wh

#----------------------------------------------------------#
#     definition : new query for HomeWizard SOCKET         #
#----------------------------------------------------------#
def read_homewizard_SOCKET(counter):
    try:
        response = urllib.request.urlopen(counter)
        data = json.loads(response.read())
        log (response, 'info')
        log (data, 'info')
        active_power_w = int((data['active_power_l1_w']))
        total_power_import_wh = int(1000*(data['total_power_import_t1_kwh']))
        #log ('Status')
        #log ("Active power: " + str(active_power_w))
        #log ("Total power In T1: " + str(int(total_power_import_wh)))
    except:
        log('Homewizard SOCKET not reachable please take action','error')
        active_power_w = 0
        total_power_import_wh = 'Null'
    finally:
        return active_power_w, total_power_import_wh

#----------------------------------------------------------#
#     definition : calculate delta between old and new     #
#                  counter                                 #
#----------------------------------------------------------#
def get_delta(counter,newvalue):
    try:
        delta = 0
        if not os.path.exists(counter):
           target = open(counter, 'w')
           target.write(str(newvalue))
           target.close()
           delta = newvalue 
           log("File " + counter + " don't exist. Creating the file",'warning')
        elif (newvalue != 0):
           target = open(counter, 'r')
           lines = target.readlines()
           oldvalue = int(lines[0]) 
           delta = newvalue - oldvalue
           target.close()
           target = open(counter, 'w+')
           target.write(str(newvalue))
           target.close()
           #delta = newvalue - oldvalue 
    except:
        log('issue with delta calculation','warning')
        return '0'
    finally:
        return delta

#----------------------------------------------------------#
#             code principal                               #
#----------------------------------------------------------#
 
# initialize Raspberry GPIO and DS18B20
#os.system('sudo /sbin/modprobe w1-gpio')
#os.system('sudo /sbin/modprobe w1-therm')
#time.sleep(2)
if len(sys.argv) > 1:
   debug = sys.argv[1]
#else:
#   print ("pas d'arguments")
d1 = datetime.datetime.now()
d2 = d1.replace(minute=5*(d1.minute // 5), second=0, microsecond=0)
log (d1, 'info')
#log (d2)
startHP = d2.replace(hour=7, minute=2, second=0, microsecond=0)
startHC = d2.replace(hour=22, minute=2, second=0, microsecond=0)
#log (startHP)
#log (startHC)
datebuff = d2.strftime('%Y-%m-%d %H:%M:00') #formating date for mySQL
 
"""for (i, counter) in enumerate(counters):
    newvalue = read_counter(counter)
    delta = get_delta(olds[i],newvalue)
    counters[i] = delta"""
counters1 = read_SMA(counter1)
counters2 = read_SMA(counter2)
log ("Read value SMA ", 'info')
log (counters1, 'info')
log (counters2, 'info')
SMA1 = get_delta(old1,counters1[1])
SMA2 = get_delta(old2,counters2[1])
#log ("Delta SMA1 " +  str(SMA1))
#log ("Delta SMA2 " +  str(SMA2))
counters3 = read_homewizard_P1(counter3)
log ("Read value P1", 'info')
log (counters3, 'info')
last_production = counters1[0]+counters2[0]
last_power = counters3[0]
last_conso =  last_production + last_power
#log ("last_production " + str(last_production))
#log ("last_conso " + str(last_conso))
#log ("last_power " + str(last_power))
TPI1 = get_delta(old3,counters3[1])
TPI2 = get_delta(old4,counters3[2])
TPO1 = get_delta(old5,counters3[3])
TPO2 = get_delta(old6,counters3[4])
#log ("delta TPI1 " + str(TPI1)) 
#log ("delta TPI2 " + str(TPI2))
#log ("delta TPO1 " + str(TPO1))
#log ("delta TPO2 " + str(TPO2))

counters4 = read_homewizard_SDM230(counter4)
log ("Read value Chauffe Eau ", 'info')
log (counters4, 'info')
last_power = counters4[0]
TPI3 = get_delta(old7,counters4[1])
#log ("delta TPI1 " + str(TPI3)) 

counters5 = read_homewizard_SOCKET(counter5)
log ("Read value Socket ", 'info')
log (counters5, 'info')
last_power = counters5[0]
TPI5 = get_delta(old9,counters5[1])
log ("delta TPI5 " + str(TPI5), 'info') 

counters6 = read_homewizard_SDM230(counter6)
log ("Read value Jacuzzi", 'info')
log (counters6, 'info')
last_power = counters6[0]
TPI6 = get_delta(old10,counters6[1])
log ("delta TPI6 " + str(TPI6), 'info') 

sql="INSERT INTO PiSolar (date, S1, S2) VALUES ('" + datebuff + "','" + str(SMA1) + "','" + str(SMA2) + "')"
log ("SQL Solar: " + sql, 'info')
query_db(sql) # on INSERT dans la base
sql="UPDATE `PiCompteur` SET `TPI1` = '" + str(counters3[1]) + "', `TPI2` = '" + str(counters3[2]) + "', `TPO1` = '" + str(counters3[3]) + "', `TPO2` = '" + str(counters3[4]) + "' WHERE 1"
log ("SQL Compteur: " + sql, 'info')
query_db(sql) # on INSERT dans la base
sql="UPDATE `PiElecPower` SET `SMA` = '" + str(counters1[0]+counters2[0]) + "', `HWZ` = '" + str(counters3[0]) + "', `CONSO` = '" + str(counters1[0]+counters2[0]+counters3[0]) + "' WHERE 1"
log ("SQL Power: " + sql, 'info')
query_db(sql) # on INSERT dans la base
if (d2.weekday() >= 5) or (d2 < startHP) or (d2 > startHC):
	log ("Heures Creuses", 'info')
	HC1 = SMA1 + SMA2 + TPI2 - TPO2
	#log (HC1)
	HP1 = 0
	sql="INSERT INTO PiElec (date, HC1, HP1, HC2, HP2, HC3, HP3, HC4, HP4, HC10, HP10) VALUES ('" + datebuff + "','" + str(HC1) + "','0','" + str(TPI3) + "','0','" + str(TPI6) + "','0','0','0','" + str(TPI5) + "', '0')"
	log ("SQL HC " + sql, 'info')
else:
	log ("Heures Pleines", 'info')
	HP1 = SMA1 + SMA2 + TPI1 - TPO1
	#log (HP1)
	HC1 = 0
	sql="INSERT INTO PiElec (date, HC1, HP1, HC2, HP2, HC3, HP3, HC4, HP4, HC10, HP10) VALUES ('" + datebuff + "','0','" + str(HP1) + "','0','" + str(TPI3) + "','0','" + str(TPI6) + "','0','0','0','" + str(TPI5) + "')"
	log ("SQL HP " + sql, 'info')
query_db(sql) # on INSERT dans la base

