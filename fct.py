# -*- coding: utf-8 -*-


import time
import requests
import urllib.parse
import hashlib
import hmac
import base64
import sys
import fct
import mysql.connector
import json
import time
import kraken
import numpy as np
import datetime

sys.path.append( "lib" )

from sshtunnel import SSHTunnelForwarder

SSH_HOST = ""
SSH_USERNAME = ""
SSH_PASSWORD = ""
now = datetime.now()

try:
  tunnel = SSHTunnelForwarder((SSH_HOST, 2222), ssh_password=SSH_PASSWORD, ssh_username=SSH_USERNAME,
       remote_bind_address=('127.0.0.1', 3306) )
  tunnel.start()
except Exception as e:
  print( "Anomalie : " )
  print( e )
  sys.exit( 1 )

mydb = mysql.connector.connect(
  host="127.0.0.1",
  port=tunnel.local_bind_port,
  user="",
  password="",
  database=""
)

mycursor = mydb.cursor(dictionary=True)


#ajouter ordres en gardant des traces
def AddOrder(data):
    rep = k.private("AddOrder", data)
    result = rep["result"] 
    pair=data["pair"]
    ticker = k.public(Ticker,data["pair"])
    res = ticker["result"]
    info_ticker = res[pair]
    if (rep["error"]==[]):
        if (data["type"]=="buy"):
            mycursor.execute("INSERT INTO Crypto (type,quantité_jetons,pair,statut,prix_total,TXID,prix_jeton) VALUES ('achat',%s,%s,'en attente',%s,%s,%s)", data["volume"], data["pair"], data["price"], result["txid"], info_ticker["b"])
        if (data["type"]=="sell"):
            mycursor.execute("INSERT INTO Crypto (type,quantité_jetons,pair,statut,prix_total,TXID,prix_jeton) VALUES ('vente',%s,%s,'en attente',%s,%s,%s)", data["volume"], data["pair"], data["price"], result["txid"], info_ticker["a"])
    return rep

#mise à jour du statut des ordres
def UpdateBdd():
    data={}
    THis = k.private(TradesHistory,data)
    mycursor.execute("SELECT TXID FROM Crypto WHERE statut='en attente';")
    rep = mycursor.fetchall()
    for trade in rep:
        if (trade in THis):
            mycursor.execute("UPDATE Crypto SET statut='achevé' WHERE TXID=%s;",trade)    
    return 0

#récupération des ordres déjà passés
def recup():
    data = {}
    THis = k.private(TradesHistory,data)
    mycursor.execute("SELECT TXID FROM Crypto")
    rep = mycursor.fetchall()
    for trade in THis:
        if (trade in rep == 0):
            mycursor.execute("INSERT INTO Crypto (type,quantité_jetons,pair,statut,prix_total,TXID,prix_jeton) VALUES (%s,%s,%s,'achevé',%s,%s,%s)",data["type"] ,data["volume"], data["pair"], data["price"], result["txid"], data["pair"])
    return 0    
    



'''def BuySell(mise, gain, pair, nbOrder):
    rep = k.private(Balance)
    eur = rep["ZEUR"]
    rep2 = k.private(Balance)
    token = rep2[pair]
    n = 1
    for k in range(nbOrder):
        if (n == 1):            
            dataBuy = {"nonce" : 1, "ordertype" : "limit", "type" : "buy", "pair" : pair, "volume" : gain/nbOrder, "price" : (gain/nbOrder)/eur }
            b = AddOrder(dataBuy)

            res = b["result"]
            txid = res["txid"]
            rep1 = k.private(Balance)
            eur = rep["ZEUR"]
            rep2 = k.private(Balance)
            token = rep2[pair]
            n = 0
        
        if (n == 0):    
            dataSell = {"nonce" : 1, "ordertype" : "limit", "type" : "sell", "pair" : pair, "volume" : token, "price" : 1 }
            s = AddOrder(dataSell)

            res = s["result"]
            txid = res["txid"]

            rep = k.private(Balance)
            eur = rep["ZEUR"]
            rep2 = k.private(Balance)
            token = rep2[pair]
            n = 1
    return 0'''
        
def MajPlanning(strat, pair, volume):
    mycursor.execute("SELECT * FROM planning WHERE statut = 0;")
    res = mycursor.fetchall()
    if (res.size() == 0):
        if (strat == token):
            mycursor.execute("SELECT type FROM planning WHERE ordre = (SELECT MAX(ordre) FROM planning);")
            LastType = mycursor.fetchall()
            if (LastType == "buy"):
                CurrentType = "sell"
                mycursor.execute("INSERT INTO planning (statut,date,type,data) VALUES (0,%s,%s,%s);" , now.strftime("%H:%M:%S"), CurrentType, Data_creator_eur(CurrentType, pair, volume))
            else:
                CurrentType = "buy"
                mycursor.execute("INSERT INTO planning (statut,date,type,data) VALUES (0,%s,%s,%s);" , now.strftime("%H:%M:%S"), CurrentType, Data_creator_eur(CurrentType, pair, volume)) 
        


        if (strat == euros):
            data = {"nonce" : 1, "ordertype" : "limit", "type" : "buy", "pair" : pair, "volume" : token, "price" : 1}


#entrées dans le planning
def Data_creator_eur(ordertype, pair, volume):
    rep = k.private(Balance)
    eur = rep["ZEUR"]
    rep2 = k.private(Balance)
    token = rep2[pair]
    if (ordertype == "buy"):
        mycursor.execute("SELECT prix_jeton FROM Crypto WHERE pair = %s ORDER BY id_transaction DESC;" , pair)
        res = mycursor.fetchone()
        price = res * 0,95       #5% moins que la derniere transaction de la meme pair (à chercher dans prix_jeton de crypto du dernier id_transaction de la pair)
    if (ordertype == "sell"):
        mycursor.execute("SELECT prix_jeton FROM Crypto WHERE pair = %s ORDER BY id_transaction DESC;" , pair)
        res = mycursor.fetchone()
        price = res * 1,05       #5% plus que la derniere transaction de la meme pair (à chercher dans prix_jeton de crypto du dernier id_transaction de la pair)
    data = {"nonce" = 1, "ordertype" = ordertype, "pair" = pair, "volume" = volume, "price" = price }
    return data

"""def Data_creator_token(ordertype, pair, price):
    rep = k.private(Balance)
    eur = rep["ZEUR"]
    rep2 = k.private(Balance)
    token = rep2[pair]
    if (ordertype == "buy"):
        mycursor.execute("SELECT prix_jeton FROM Crypto WHERE pair = %s ORDER BY id_transaction DESC;" , pair)
        res = mycursor.fetchone()
               #5% moins que la derniere transaction de la meme pair (à chercher dans prix_jeton de crypto du dernier id_transaction de la pair)
    if (ordertype == "sell"):
        mycursor.execute("SELECT prix_jeton FROM Crypto WHERE pair = %s ORDER BY id_transaction DESC;" , pair)
        res = mycursor.fetchone()
        price = res * 1,05       #5% plus que la derniere transaction de la meme pair (à chercher dans prix_jeton de crypto du dernier id_transaction de la pair)
    data = {"nonce" = 1, "ordertype" = ordertype, "pair" = pair, "volume" = volume, "price" = price }
    return data"""
    
#passage de commande à partir du planning
def Defilement_planning():
    mycursor.execute("SELECT data FROM planning WHERE statut = 0 ORDER BY ordre ASC;")
    rep = mycursor.fetchone()
    AddOrder(rep)
    mycursor.execute("SELECT ordre from planning where statut = 0 ORDER BY ordre ASC;")
    ordre = mycursor.fetchone()
    mycursor.execute("UPDATE planning SET statut = 1 WHERE ordre = %s;", ordre)
    return 0