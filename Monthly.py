#!/usr/bin/python
# -*- coding: utf-8 -*-
 
#=========================================================================
#              Monthly.py
#-------------------------------------------------------------------------
# by Bruno Faucon - 2022
# version 0.1 2022-10-03
# Cleaning code
#-------------------------------------------------------------------------
# Script Updating Monthly summary 
#-------------------------------------------------------------------------
#===================================================================
 
#----------------------------------------------------------#
#             package importation                          #
#----------------------------------------------------------#
import os
import time
import datetime
import MySQLdb   # MySQLdb must be installed by yourself
from threading import Timer
#import sqlite3
 
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

#----------------------------------------------------------#
#             Variables                                    #
#----------------------------------------------------------#

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
#             Primary Code                                 #
#----------------------------------------------------------#
sql="CALL `MonthlyElec`();"
query_db(sql) 
sql="CALL `MonthlyWater`();"
query_db(sql) 
sql="CALL `MonthlySolar`();"
query_db(sql) 
