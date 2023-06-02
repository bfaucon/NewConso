#!/usr/bin/python
# -*- coding: utf-8 -*-
 
#=========================================================================
#              water_test.py
#-------------------------------------------------------------------------
# version 0.1 2014-06-16
# Modifications done by Bruno Faucon - 2020
# version 0.3 2020-05-06
# connection au sql synology
# Modifications done by Bruno Faucon - 2022
# version 0.4 2022-04-20
# test console + Email for alerting
# version 0.5 2023-06-02
# Move to new Raspberry
#-------------------------------------------------------------------------
# Script checking the water consumption in last interval of time.
# If greater than treashold, then send an Email for warning
#
# tested with python 2.7 on Raspberry pi (wheezy) and MariaDB 5.5.34 on NAS Synology DS411J (DSM 5)
#-------------------------------------------------------------------------
#=========================================================================
 
#----------------------------------------------------------#
#             package importation                          #
#----------------------------------------------------------#
import os
import smtplib
import time
import datetime
import MySQLdb   # MySQLdb must be installed by yourself
from threading import Timer
from SendMail import *

#-----------------------------------------------------------------#
#  constants : use your own values / utilisez vos propres valeurs #
#-----------------------------------------------------------------#
PATH_THERM = "/home/pi/consumption/" #path to this script
PATH_LOG = "/home/pi/consumption/log" #path to this script
DB_SERVER ='192.168.2.10'  # MySQL : IP server (localhost if mySQL is on the same machine)
DB_USER='conso'     # MySQL : user
DB_PWD='WXH.Yrb24RdU'            # MySQL : password
DB_BASE='consumption'     # MySQL : database name
DB_PORT=3307     # MySQL : database port
EMAIL_SMTP='smtp.famillefaucon.be'
EMAIL_PORT=587
EMAIL_LOGIN='brfa@famillefaucon.be'
EMAIL_PWD='lufa45mail'
EMAIL_FROM='rpi@one2care.be'
EMAIL_TO='bruno.faucon@one2care.be'
# Alert Limit = treshold for Water consumption 
# 150/15 means Send alert if more than 150L consumption on 15 min timeframe.
ALERT_LIMIT = 150
ALERT_TIME = 15

#----------------------------------------------------------#
#             Variables                                    #
#----------------------------------------------------------#
conso=0.00
debug = False

#----------------------------------------------------------#
#     definition : database query                          #
#----------------------------------------------------------#
def query_db(sql):
    db = MySQLdb.connect(DB_SERVER, DB_USER, DB_PWD, DB_BASE, DB_PORT)
    cursor = db.cursor()
    cursor.execute(sql)
    a = cursor.fetchone()  
    t = int(a[0])
    return t
    db.close() 

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
#     Primary code                                         #
#----------------------------------------------------------#
if len(sys.argv) > 1:
   debug = sys.argv[1]
#Lecture de la consommation sur le dernier intervale
sql="SELECT sum(W1) as W1 FROM `PiWater` WHERE date > NOW() - INTERVAL " + str(ALERT_TIME) + " MINUTE"
#print (sql)
conso = query_db(sql)
# test forcer 
# conso = ALERT_LIMIT + 10
if conso > ALERT_LIMIT:
   EMAIL_TEXT = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") +": La consommation sur les " + str(ALERT_TIME) + " dernieres minutes est anormales (" + str(conso) + "L), merci de verifier s'il n'y a pas un robinet ouvert."
   a = log(EMAIL_TEXT, 'error')
else:
   EMAIL_TEXT = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") +": La consommation est normale sur les " + str(ALERT_TIME) + " dernieres minutes : " + str(conso) + "L."
   a = log(EMAIL_TEXT, 'info')

