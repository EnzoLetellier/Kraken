import sys
import fct
import mysql.connector
import json
import time
import testKraken
import base64

sys.path.append( "lib" )

from sshtunnel import SSHTunnelForwarder

SSH_HOST = ""
SSH_USERNAME = ""
SSH_PASSWORD = ""

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

#traitement
mycursor = mydb.cursor(dictionary=True)
mycursor.execute("SELECT * FROM Crypto")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)


# Read Kraken API key and secret stored in environment variables
api_url = "https://api.kraken.com"

api_key = open("API_Public_Key.txt").read().strip()
api_sec = base64.b64decode(open("API_Private_Key.txt").read().strip())

data ={
    "nonce": str(int(1000*time.time())),
    "trades": True
    }

# Construct the request and print the result
resp = fct.kraken_request('/0/private/TradesHistory', 
data, api_key, api_sec)

print(resp.json())

