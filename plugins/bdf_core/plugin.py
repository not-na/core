#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plugin.py
#  
#  Copyright 2014 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
"""
#import core

JSON_MODE = False

try:
    import json
except ImportError:
    print("Couldn't load json as extension for BDF.")

class DecodingError(IOError):
    pass
class InvalidTypeError(DecodingError):
    pass
class EncodingError(IOError):
    pass

TOKEN_NONE = "0000"
TOKEN_BYTE = "0001"
TOKEN_INT  = "0010"
TOKEN_LONG = "0011"
TOKEN_STRING="0100"
TOKEN_BOOL = "0101"
TOKEN_LIST = "0110"
TOKEN_STLIST="0111"
TOKEN_DICT = "1000"

def _extractName(data):
    try:
        return data[8:(int("0b"+data[4:8]))*8]
    except Exception:
        return ""
def _getStartPos(data,n=True,t=True):
    if n and t:
        return 4+(int("0b"+data[4:8])*7)
    elif n and not t:
        return int("0b"+data[4:8])*7
    elif not n and t:
        return 4
    elif not n and not t:
        return 0
_gs = _getStartPos
def _le(olen,data):
    return olen+_getStartPos(data)

def decoder_none(data,n=True,t=True):
    return [_le(0,data),None,_extractName(data)]
def decoder_byte(data,n=True,t=True):
    d = int("0b"+data[_gs(data,n,t):_gs(data,n,t)+8])
    return [_le(8,data),d,_extractName(data)]
def decoder_int(data,n=True,t=True):
    d = int("0b"+data[_gs(data,n,t):_gs(data,n,t)+32])
    return [_le(32,data),d,_extractName(data)]
def decoder_long(data,n=True,t=True):
    d = int("0b"+data[_gs(data,n,t):(int("0b"+data[_gs(data,n,t):_gs(data,n,t)+16]))*8])
    d2 = _le(int("0b"+data[_gs(data,n,t):_gs(data,n,t)+16])*8,data)
    return [d2,d,_extractName(data)]
def decoder_string(data,n=True,t=True):
    d = data[_gs(data,n,t):(int("0b"+data[_gs(data,n,t):_gs(data,n,t)+16]))*8]
    return [_le(int("0b"+data[_gs(data,n,t):_gs(data,n,t)+16])*8,data),d,_extractName(data)]
def decoder_bool(data,n=True,t=True):
    d = data[_gs(data,n,t):_gs(data,n,t)+1]
    return [_le(1,data),bool(d),_extractName(data)]
def decoder_list(data,n=True,t=True):
    g = _gs(data,n,t)
    dllen = int("0b"+data[g:g+32])
    dlen = 0
    d = []
    dr = data[g+32:g+32+dllen]
    co = g+32
    while True:
        ddata = data[co:]
        r = TOKEN2DEC[ddata[:4]](ddata,False)
        rd = r[1]
        rlen = r[0]
        d.append(rd)
        co+=rlen
        if co >= dlen:
            break
    return [_le(dlen,data),d,_extractName(data)]
def decoder_stlist(data,n=True,t=True):
    g = _gs(data,n,t)
    dllen = int("0b"+data[g:g+32])
    dlen = 0
    d = []
    dr = data[g+32:g+32+dllen]
    co = g+36
    dt = data[g+32:g+36]
    f = TOKEN2DEC[dt]
    while True:
        ddata = data[co:]
        r = f(ddata,False,False)
        rd = r[1]
        rlen = r[0]
        d.append(rd)
        co+=rlen
        if co >= dlen+g+36:
            break
    return [_le(dlen,data),d,_extractName(data)]
def decoder_dict(data,n=True,t=True):
    g = _gs(data,n,t)
    dllen = int("0b"+data[g:g+32])
    dlen = 0
    d = {}
    dr = data[g+32:g+32+dllen]
    co = g+36
    dt = data[g+32:g+36]
    f = TOKEN2DEC[dt]
    while True:
        ddata = data[co:]
        r = f(ddata,True,False)
        rd = r[1]
        rlen = r[0]
        d[r[2]] = rd
        co+=rlen
        if co >= dlen+g+36:
            break
    return [_le(dlen,data),d,_extractName(data)]

TOKEN2DEC = {TOKEN_NONE:decoder_none,
             TOKEN_BYTE:decoder_byte,
             TOKEN_INT:decoder_int,
             TOKEN_LONG:decoder_long,
             TOKEN_STRING:decoder_string,
             TOKEN_BOOL:decoder_bool,
             TOKEN_LIST:decoder_list,
             TOKEN_STLIST:decoder_stlist,
             TOKEN_DICT:decoder_dict}

def _bin2txt(data):
    out = ""
    data = _group(data,8)
    for d in data:
        out+=chr(int("0b"+d))
    return out
def _group(data,n):
    co = 0
    out = []
    while co <=len(data)-n:
        out.append(data[co:co+n])
        co+=n
    return out
def _encData(payload,name,ctype,n,t):
    if n and t:
        nl = len(name)/8
        ns = str(nl)+_txt2bin(name)
        return ctype+ns+payload
    elif n and not t:
        nl = len(name)/8
        ns = nl+_txt2bin(name)
        return ns+payload
    elif not n and t:
        return ctype+payload
    elif not n and not t:
        return payload
def _aBin(data,s):
    data = bin(int(data))
    data =  data.lstrip("0").lstrip("b")
    return data.rjust(s,"0")
def _txt2bin(data):
    out = ""
    for char in data:
        out+=bin(ord(char)).lstrip("0").lstrip("b")
    return out

def encoder_none(data,name="",n=True,t=True):
    return _encData("",name,TOKEN_NONE,n,t)
def encoder_byte(data,name="",n=True,t=True):
    return _encData(_aBin(data,8),name,TOKEN_BYTE,n,t)
def encoder_int(data,name="",n=True,t=True):
    return _encData(_aBin(data,32),name,TOKEN_INT,n,t)
def encoder_long(data,name="",n=True,t=True):
    rd = bin(data).lstrip("0").lstrip("b")
    dl = _aBin(len(rd),32)
    d = dl+rd
    return _encData(d,name,TOKEN_LONG,n,t)
def encoder_string(data,name="",n=True,t=True):
    l = len(data)
    return _encData(_aBin(l,16)+_txt2bin(data),name,TOKEN_STRING,n,t)

TOKEN2ENC = {TOKEN_NONE:encoder_none,
             TOKEN_BYTE:encoder_byte,
             TOKEN_INT:encoder_int,
             TOKEN_LONG:encoder_long,
             TOKEN_STRING:encoder_string,
             }


class BDF():
    def __init__(self):
        pass
    def save(self,data,fname):
        d = self.encode(data)
        f = open(fname,"wb")
        f.write(d)
        f.close()
    def encode(self,data):
        out = ""
        for k in data:
            t = self._checkType(k,data[k])
            out+=self._encodeSingleToken(k,data[k],t)
        return self._bin2txt(out)
    def load(self,fname):
        f = open(fname,"rb")
        data = f.read()
        f.close()
        data = self._txt2bin(data)
        out = {}
        while len(data)>=1:
            r = self._decodeSingleToken(data)
            data = r[1]
            out[r[2]] = r[1]
        return out
    def decode(self,data):
        data = self._txt2bin(data)
        out = {}
        while len(data)>=1:
            r = self._decodeSingleToken()
            data = r[1]
            out[r[2]] = r[1]
        return out
    def _txt2bin(self,data):
        out = ""
        for char in data:
            out+=bin(ord(char)).lstrip("0").lstrip("b")
        return out
    def _decodeSingleToken(self,data):
        if data[:4] not in TOKEN2DEC:
            raise InvalidTypeError("[BDF] Type %s not found"%data[:4])
        r = TOKEN2DEC[data[:4]](data)
        data = data[r[0]:]
        return [r[1],data,r[2]]
    def _bin2txt(self,data):
        out = ""
        data = self._group(data,8)
        for d in data:
            out+=chr(int("0b"+d))
        return out
    def _group(self,data,n):
        co = 0
        out = []
        while co <=len(data)-n:
            out.append(data[co:co+n])
            co+=n
        return out
    def _checkType(self,k,v):
        if isinstance(v,int):
            if v < 255:
                return TOKEN_BYTE
            return TOKEN_INT
        elif isinstance(v,str):
            return TOKEN_STRING
        elif isinstance(v,long):
            return TOKEN_LONG
        elif isinstance(v,bool):
            return TOKEN_BOOL
        elif v == None:
            return TOKEN_NONE
        elif isinstance(v,list):
            t = 0
            for i in v:
                if t == 0:
                    t = self._checkType("",i)
                elif t != 0 and self._checkType("",i)!=t:
                    return TOKEN_LIST
            return TOKEN_STLIST
        elif isinstance(v,dict):
            return TOKEN_DICT
    def _encodeSingleToken(self,k,v,t):
        f = TOKEN2ENC[t]
        d = f(v,k)
        return d

class BDF_jsonEmulate():
    def __init__(self):
        pass
    def save(self,data,fname):
        json.dump(data,open(fname,"w"))
    def encode(self,data):
        return json.dumps(data)
    def load(self,fname):
        return json.load(open(fname,"r"))
    def decode(self,data):
        return json.loads(data)

if JSON_MODE:
    BDF = BDF_jsonEmulate
"""

import collections
import decimal

import core

# Important Constants
# If you change those, you will probably not be able to load encoded data

FLOAT_STRUCT = "f" # Should never be needed to be modified; used for the float de- and encoders
FLOAT_ALLOW_DECIMAL = True

INT_MAX = 2**31-1 # Equals 32-bit Python's sys.maxint
INT_BITS = 32 # Amount of bits needed

BYTE_MAX = 2**8-1 # The maximum number a element of type byte can be
BYTE_BITS = 8

LONG_LENGTH_BITS = 32 # Bits used to declare a long's length in bits

STR_LENGTH_BITS = 64 # Bits used to declare a string's length in chars

DICT_FINISHING_DATA = None # Will be used as last element of a dict to signify its end, should be unnamed.

class BinArrayError(Exception):pass # Used for various BinArray-related errors

class BinArray():
    def __init__(self,obj=None):
        if obj == None:
            self.data = []
        elif isinstance(obj,str):
            self.data = []
            for c in str:
                self.data.extend(list(bin(ord(c)).lstrip("0").lstrip("b")))
        elif isinstance(obj,int):
            self.data = []
            self.data.extend(list(bin(obj).lstrip("0").lstrip("b")))
        elif isinstance(obj,bool):
            self.data = [int(obj)]
        elif isinstance(obj,list):
            self.data = []
            for i in obj:
                self.data.append(int(i))
        else:
            raise TypeError("Object %s can't be used in BinArray"%obj)
    def append(self,obj):
        if isinstance(obj,BinArray):
            self.data.extend(obj.data)
        else:
            self.data.append(obj)
    def delete(self,start,end):
        del self.data[start:end]
    def get(self,v1=-1,v2=-1):
        if v1==-1 and v2 == -1:
            raise ValueError("not enough arguments for BinArray.get!")
        elif v1!=-1 and v2==-1:
            v2 = v1
            v1 = 0
        d = BinArray(0)
        d.data = self.data[v1:v2]
        return d
    def getBitAt(self,n):
        return bool(self.data[n])
    def __len__(self):
        return len(self.data)
    def __int__(self):
        return int("0b"+"".join(self.data),base=2)
    def __str__(self):
        if self.data == []:
            return ""
        out = ""
        c = 0
        d = self.data[:]
        while len(d)>=1:
            c+=1
            if c>8:
                c=0
                d2 = d[:7]
                out+=chr(int("0b"+"".join(d2)))
                del d[:7]
        if c<=8:
            out+=chr(int("0b"+"".join(d)))
        return out
    def __eq__(self,other):
        if isinstance(other,BinArray):
            return self.data == other.data
        elif isinstance(other,str):
            return self.__str__()==other
        elif isinstance(other,list):
            return self.data == other
        else:
            raise TypeError("Can't compare BinArray with obj of type %s"%type(other))
    def __hash__(self):
        return self.__int__()
    def __ne__(self,other):
        return not self.__eq__(other)
    def __nonzero__(self):
        return self.__int__()!=0
    def __add__(self,other):
        return BinArray(int(self)+int(other))

PADBIT = BinArray(0)

bdfDecoders = core.ServiceManager()
bdfEncoders = core.ServiceManager()

bdfTypeResolvers = collections.OrderedDict() # Dict with key=resolverFunc and if resolverFunc returns true, the type is assumed to be the value

# Style Note: first X: resolver done
#             second X: encoder done
#             third X: decoder done
# use a "." if halfdone/not tested

bdfBinTypes = {BinArray(0):"none", ##   XXX # Dict with key=BinArray to match with type and key=string repr of the type
               BinArray(1):"bool", ##   XX-
               BinArray(2):"int", ##    X.-
               BinArray(3):"byte", ##   X--
               BinArray(4):"str", ##    X--
               BinArray(5):"long", ##   X--
               BinArray(6):"dict", ##   X--
               BinArray(7):"list", ##   X--
               BinArray(8):"stlist", ## X-- # List containing items all of the same type
               BinArray(9):"float", ##  X-- # Floats will be en-/decoded using struct with the constant FLOAT_STRUCT defined above
               }

bdfStrTypes = {}
for k in bdfBinTypes: # To automatically build the inverted table
    bdfStrTypes[bdfBinTypes[k]]=k

# BDF_CORE: Base Type Resolvers

# Resolver API:
# resolver func gets called with the plain object and should return any equivalent of True if the variable is of the type the resolver is named after
# resolvers should be registered in bdfTypeResolvers with the key being the function and the value being the type in string format; eg: resolver_none:"none"
# resolvers are stored in OrderedDicts, so resolvers that are registered first, should be called first, but you should not rely on this; alternative implementations my change this.

def resolver_none(data):
    return data == None
bdfTypeResolvers[resolver_none]="none"
def resolver_bool(data):
    return data in [True,False]
bdfTypeResolvers[resolver_bool]="bool"
def resolver_int(data):
    return isinstance(data,int) and BYTE_MAX<data<=INT_MAX or -INT_MAX<data<0
bdfTypeResolvers[resolver_int]="int"
def resolver_str(data):
    return isinstance(data,str)
bdfTypeResolvers[resolver_str]="str"
def resolver_byte(data):
    return isinstance(data,int) and 0 <= data <= BYTE_MAX
bdfTypeResolvers[resolver_byte]="byte"
def resolver_long(data):
    return isinstance(data,int) and data > INT_MAX or data < (-INT_MAX)
bdfTypeResolvers[resolver_long]="long"
def resolver_dict(data):
    return isinstance(data,dict)
bdfTypeResolvers[resolver_dict]="dict"
def resolver_list(data):
    return isinstance(data,list) and not resolver_stlist(data)
bdfTypeResolvers[resolver_list]="list"
def resolver_stlist(data):
    if not isinstance(data,list):
        return False
    t = -1
    e = Encoder()
    for i in data:
        if t == -1:
            t = int(e.resolveType(i))
        elif int(e.resolveType(i))!=t:
            return False
        elif int(e.resolveType(i))==t:
            pass
    return True
bdfTypeResolvers[resolver_stlist]="stlist"
def resolver_float(data):
    return isinstance(data,float) or (FLOAT_ALLOW_DECIMAL and isinstance(data,decimal.Decimal))
bdfTypeResolvers[resolver_int]="float"



# BDF_CORE: Base Encoders

# Encoder API:
# function gets called with the plain input data
# returns instance of BinArray or subclass, containing the encoded data excluding type or name
# encoders should be registered as services in bdfEncoders, the service name should be of format "bdf_encoder_[type]"
# the type of an object is guessed via bdfTypeResolvers; go to BDF_CORE: Base Type Resolvers for more information

def encoder_none(data):
    return BinArray()
bdfEncoders.add_service(core.Service("bdf_encoder_none","bdf_core.encoder_none",encoder_none))
def encoder_bool(data):
    return BinArray(data)
bdfEncoders.add_service(core.Service("bdf_encoder_bool","bdf_core.encoder_bool",encoder_bool))
def encoder_int(data):
    d = BinArray()
    b = BinArray(data)
    d+(BinArray([0 for i in len(b)]))
    d+BinArray(data)
    return d
bdfEncoders.add_service(core.Service("bdf_encoder_int","bdf_core.encoder_int",encoder_int))

# BDF_CORE: Base Decoders

# Decoder API:
# function gets called with dict data as input
# dict data contains following keys:
#  - bin: BinArray or subclass containing the raw binary data; a decoder should not modify this object.
#  - name: string version of the name of the object to decode; will be None if the object doesn't have one
#  - type: string version of the type as resolved using bdfTypeResolvers
#  - parent: object that represents the parent; none if this object is at the root; this object may not be fully decoded or usable
#  - decoder: reference back to the decoder; intended for use in nested structures
# returns a dict containing following keys:
#  - result: Object that represents the given input data, this object is the main output
#  - usedbits: Amount of bits this object required to be stored, without type or name; used to calculate offset for the next object
#  - success: Bool representing if the decoding was successfull; if false, all other keys except errmsg need not to be defined
#  - errmsg: String that, if success is false, will be printed out; this must not be defined if success is true.
# note that a decoder could also raise exceptions directly, if you are making an alternative implementation, please be aware of that
# the usedbits key of the returned dict can be any integer value >=0; eg. for decoder_none it is always 0.
# a decoder should be registered as a service in bdfDecoders with the name being of the format "bdf_decoder_[type]".
# a decoder can handle multiple types of objects at once, eg. you could just define one, big decoder that uses the type attr of the input data
# to determine the exact type, however it is not recommended do do that
# in the future i may switch over to classes for de- and encoders, however this seems to be too much work.

def decoder_none(self,data):
    return {"result":None,"usedbits":0,"success":True}
bdfDecoders.add_service(core.Service("bdf_decoder_none","bdf_core.decoder_none",decoder_none))
def decoder_bool(self,data):
    return {"result":data.getBitAt(0),"usedbits":1,"success":True}
bdfDecoders.add_service(core.Service("bdf_decoder_bool","bdf_core.decoder_bool",decoder_bool))


class BDFError(RuntimeError):pass
class EncodingError(BDFError):pass
class NoEncoderError(EncodingError):pass
class NoResolverError(EncodingError):pass
class NameToLongError(EncodingError):pass
class DecodingError(BDFError):pass
class InvalidTypeError(DecodingError):pass
class InvalidLengthError(DecodingError):pass
class InvalidDataError(DecodingError):pass

class Decoder():
    def parse(self,data):
        d = BinArray(data)
        return self.decodeBase(d)
    def decodeBase(self,b):
        t = self.resolveType(b)
        n = self.getName(b,typed=True)
        d = self.extractData(b)
        return self.decodeObject(d,t,n)
    def decodeObject(self,data,t,name=None):
        return self.getDecoder(t)(data,name)
    def getName(self,data,typed=True):
        pass # TODO: add Decoder.getName()
    def resolveType(self,data):
        return bdfBinTypes[data.get(0,4)]
    def getDecoder(self,t):
        return bdfDecoders.service("bdf_decoder_%s"%t)
    

class Encoder():
    def encode(self,data):
        out = self.encodeObject(data,None,True)
        return str(out)
    def resolveType(self,var,name=None):
        for f in bdfTypeResolvers:
            if f(var,name):
                return bdfTypeResolvers[f]
        raise NoResolverError("Object of type %s with name %s is not encodeable with BDF, try adding a typeResolver to bdfTypeResolvers"%(type(var),name))
    def encodeObject(self,var,name=None,typed=True):
        try:
            e = bdfEncoders.service("bdf_encoder_%s"%self.resolveType(var,name))
        except Exception:
            raise NoEncoderError("Encoder %s couldn't be found"%self.resolveType(var,name))
        try:
            d = e(var,name,typed)
            if not isinstance(d,BinArray):
                raise TypeError("Encoder returned invalid Object of type %s"%type(d))
        except Exception as exc:
            raise EncodingError("Exception while trying to encode obj of type %s with name %s"%(type(var),name))
        return d

class BDF(): # just for compatibility and simplicity
    def decode(self,data):
        return Decoder().parse(data)
    def encode(self,data):
        return Encoder().encode(data)
    def save(self,data,fname):
        d = self.encode(data)
        f = open(fname,"wb")
        f.write(d)
        f.close()
        return d
    def load(self,fname):
        f = open(fname,"rb")
        d = f.read()
        f.close()
        data = self.decode(d)
        return data

def encode(data):
    """Encodes an BDF-encodeable Object."""
    return Encoder().encode(data)
def decode(data):
    """Decodes a valid BDF string."""
    return Decoder().parse(data)
