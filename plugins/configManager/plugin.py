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

import core
import base64

STR2BOOL = {"True":True,
            "true":True,
            "TRUE":True,
            "yes":True,
            "Yes":True,
            "YES":True,
            "1":True,
            "FALSE":False,
            "False":False,
            "false":False,
            "no":False,
            "NO":False,
            "No":False,
            "0":False}

def dec_int(data):
    return int(data)
def dec_str(data):
    return str(data)
def dec_bool(data):
    return STR2BOOL[data]
def dec_b64decode(data):
    return base64.b64decode(data+"===")
def dec_b64encode(data):
    return base64.b64encode(data).rstrip("=")
def dec_bin(data):
    return int("0b"+data)
def dec_hex(data):
    return int("0x"+data)

DECODERS = {"int":dec_int,
            "str":dec_str,
            "bool":dec_bool,
            "b64decode":dec_b64decode,
            "b64encode":dec_b64encode,
            "bin":dec_bin,
            "hex":dec_hex}

def enc_int(data):
    return str(data)
def enc_str(data):
    return data
def enc_bool(data):
    return str(data)
def enc_str2(data):
    return base64.b64encode(data).rstrip("=")

ENCODERS = {"int":enc_int,
            "str":enc_str,
            "bool":enc_bool,
            "other":enc_str2}

def loadFromFile(fname):
    return Decoder(fname).decode()
def saveToFile(fname,data):
    Encoder(fname).encode2file(data)

def decode(data):
    return Decoder().decode(data)
def encode(data):
    return Encoder().encode(data)

def load(fname):
    return Decoder(fname).decode()
def dump(data,fname):
    return Encoder(fname).encode2file(data)
def loads(data):
    return decode(data)
def dumps(data):
    return encode(data)

class Decoder():
    def __init__(self,fname=None):
        self.fname = fname
        self.decoders = DECODERS
        self.val_sep = "="
    def decode(self,data=None):
        typed = False
        out = {}
        if self.fname != None:
            d = self.getRaw()
        elif self.fname == None:
            d = data
        for ds in d.split("\n"):
            if ds.startswith("meta-"):
                if ds.lower() == "meta-supports-type=true":
                    typed = True
                    continue
            elif ds.startswith("#"):
                continue
            elif ds.strip() == "":
                continue
            dss = ds.split(self.val_sep)
            if typed and len(dss)>=3:
                rtyped = DECODERS[dss[2]](dss[1])
            else:
                rtyped = dss[1]
            out[dss[0]]=rtyped
        return out
    def getRaw(self):
        f = open(self.fname,"r")
        d = f.read()
        f.close()
        return d

class Encoder():
    def __init__(self,fname=None):
        self.fname = fname
        self.val_sep = "="
    def encode(self,data):
        out = ""
        if "meta-supports-type" in data:
            data.remove("meta-supports-type")
            out = "meta-supports-type=True\n"
        for k in data:
            v = self._toStr(data[k])
            t = self._type(data[k])
            out+="{key}{valsep}{value}{valsep}{t}\n".format(key=k,valsep=self.val_sep,value=v,t=t)
        return out
    def encode2file(self,data):
        d = self.encode(data)
        f = open(self.fname,"w")
        f.write(d)
        f.close()
    def _toStr(self,d):
        if isinstance(d,str):
            if "=" not in d:
                return ENCODERS["str"](d)
            elif "=" in d:
                return ENCODERS["other"](d)
        elif isinstance(d,int):
            return ENCODERS["int"](d)
        elif d in [True,False]:
            return ENCODERS["bool"](d)
        else:
            raise TypeError("object %s can't be saved with configManager, please convert it to a built-in type first.")
    def _type(self,d):
        if isinstance(d,str):
            if "=" not in d:
                return "str"
            elif "=" in d:
                return "b64decode"
        elif isinstance(d,int):
            return "int"
        elif d in [True,False]:
            return "bool"
