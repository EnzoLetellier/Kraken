#!/usr/bin/env python3

import sys
import base64

debug = 1

sys.path.append( "lib" )

sys.tracebacklimit = 0
if debug == 1:
  sys.tracebacklimit = 1

from sshtunnel import SSHTunnelForwarder
import mysql.connector
import json
import kraken
import time
# from datetime import datetime 
import datetime

# Recuperation des clefs (API et SECRET)
try:
  api_key = open("API_Public_Key.txt").read().strip()
  api_secret = base64.b64decode(open("API_Private_Key.txt").read().strip())
except:
  print("API public key and API private (secret) key must be in text files called API_Public_Key.txt and API_Private_Key.txt")
  sys.exit(1)

# 
k = kraken.api( api_key, api_secret )


serverTime = k.getServerTime()
print( "Server time ", serverTime )

# Exemple public : Affichage de la date et de l'heure du serveur
par = { }
r = k.public( "Time", json.dumps( par ) )
if r :
  serverTime = r[ "unixtime" ]
  print( "Server time : ", datetime.datetime.fromtimestamp( serverTime ) )

# Recuperation du trades history
tsStart = time.mktime( datetime.date( 2020, 8, 1 ).timetuple( ) )
tsEnd = time.mktime( datetime.date( 2020, 8, 10 ).timetuple( ) )
ofs = -100
# print( "Debut : " + datetime.datetime.fromtimestamp( tsStart ).strftime( "%Y-%m-%d %H:%M:%S" ) + ", fin : " + datetime.datetime.fromtimestamp( tsEnd ).strftime( "%Y-%m-%d %H:%M:%S" )  )
# sys.exit( 0 )
par = { "type": "all",  "start": "tsStart", "end": tsEnd }
r = k.private( "TradesHistory", json.dumps( par ) )
trades = r[ "trades" ]
count = r[ "count" ]
for x in trades:
  key = x
  trade = trades[ key ]
  tradeTS = trade[ "time" ]
  d = datetime.datetime.fromtimestamp( tradeTS )
  data = { "Date" : d.strftime( "%Y-%m-%d %H:%M:%S" ), "pair" : trade[ "pair" ], "trade" : trade }
  print( data )
  #print( r[ "trades" ][ x ][ "time" ], " : " + d.strftime( "%Y-%m-%d %H:%M:%S" ) )


#connexion à la bdd







def calcPct( x, y ) :
  pct = ( y - x ) / x
  return pct



