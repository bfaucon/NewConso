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
# CREATE TABLE IF NOT EXISTS `PiSolar` (
#  `id` int(11) NOT NULL,
#  `date` datetime NOT NULL,
#  `S1` decimal(10,2) DEFAULT NULL,
#  `S2` decimal(10,2) DEFAULT NULL
#) ENGINE=InnoDB DEFAULT CHARSET=latin1;
# ;
# 
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
from Send_Email import *

#import sqlite3
 
