

import platform
from datetime import datetime
import sys
import json
import time, base64, hashlib, hmac, urllib.request

if int(platform.python_version_tuple()[0]) > 2:
  import urllib.request as urllib2
else:
  import urllib2


class api:

  __api_domain = "https://api.kraken.com"
  __api_public_path = "/0/public/"
  __api_private_path = "/0/private/"

  def __init__( self, API_KEY, SECRET_KEY ):
    self.__API_KEY = API_KEY
    self.__SECRET_KEY = SECRET_KEY

  def public( self, method, request ) :
    return( self.query( self.__api_public_path, method, request ) )
    pass

  def private( self, method, request ) : 
    return( self.query( self.__api_private_path, method, request ) )
    pass

  def query( self, api_path, api_method, api_data ):
    api_nonce = str( int( time.time() * 10000 ) )
    api_postdata = api_data + "&nonce=" + api_nonce
    api_postdata = api_postdata.encode( 'utf-8' )
    api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_postdata).digest()
    api_hmacsha512 = hmac.new( self.__SECRET_KEY, api_path.encode('utf-8') + api_method.encode('utf-8') + api_sha256, hashlib.sha512 )
    api_request = urllib2.Request( self.__api_domain + api_path + api_method, api_postdata )
    api_request.add_header("API-Key", self.__API_KEY )
    api_request.add_header("API-Sign", base64.b64encode(api_hmacsha512.digest()))
    api_request.add_header("User-Agent", "Kraken REST API")

    try:
      api_reply = urllib2.urlopen(api_request).read().decode()
    except Exception as error:
      print("API call failed (%s)" % error)
      sys.exit( 1 )

    jsonRes = json.loads( api_reply )
    err = jsonRes[ "error" ]
    if( err ) :
      print( api_reply )
      sys.exit( 0 )
    else:
      pass
      
    return( jsonRes[ "result" ] )

  def getServerTime( self ):
    api_method = "Time"
    api_data = ""
    api_request = urllib2.Request( self.__api_domain + self.__api_public_path + api_method + '?' + api_data)
    api_request.add_header("User-Agent", "Kraken REST API")
    try:
      api_reply = urllib2.urlopen(api_request).read()
    except Exception as error:
      print("API call failed (%s)" % error)
      sys.exit(1)

    try:
      api_reply = api_reply.decode()
    except Exception as error:
      if api_method == 'RetrieveExport':
        sys.stdout.buffer.write(api_reply)
        sys.exit(0)
      print("API response invalid (%s)" % error)
      sys.exit( 1 )

    jRet = json.loads( api_reply )
    if( jRet[ "error" ] == [] ):
      return datetime.fromtimestamp( jRet[ "result" ][ "unixtime" ] )
    else:
      raise kError( "Erreur API \n" )

    return( "" )

  def getTradesHistory( self, since, to ) :
    pass

  def test( self, msg ):
    print( msg )



class kError( Exception ):
  def __init__( self, message ):
    pass # print( message )

