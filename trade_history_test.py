# -*- coding: utf-8 -*-


import time
import fct

host = "127.0.0.1" # à changer

api_sec = ""
# Read Kraken API key and secret stored in environment variables
api_url = "https://api.kraken.com"
api_key = ""

data ={
    "nonce": str(int(1000*time.time())),
    "trades": True
    }

# Construct the request and print the result
resp = fct.kraken_request('/0/private/TradesHistory', 
data, api_key, api_sec)

print(resp.json())