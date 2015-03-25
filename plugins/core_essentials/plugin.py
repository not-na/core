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

class PluginFinderSingleFile(core.Finder):
    def __init__(self):
        core.Finder.__init__(self)
    def find(self,searchpath,name):
        r=[False,None]
        for s in searchpath:
            r = self._recfind(s,name)
            if r[0]:
                break
        if not r[0]:
            return None
        elif r[0]:
            return SingleFilePlugin(r[1],name)
    def _recfind(self,s,name):
        for p in os.listdir(s):
            if (p==name+".py" or p==name+".pyw" or p==name+".pyo")and os.path.isfile(os.path.join(s,p)):
                return [True,os.path.join(s,p)]
            elif os.path.isdir(os.path.join(s,p)):
                r = self._recfind(os.path.join(s,p),name)
                if r[0]:
                    return r
        return [False,None]

class SingleFilePlugin(core.Plugin):
    def __init__(self,fpath,name):
        core.Plugin.__init__(self,fpath,name)
    def load(self):
        d = {"core_plugin":True,"plugin_name":self.name}
        execfile(os.path.join(self.fpath),globals=d)
        self.plugobj = d["plugobj"]

class DependencyManager():
    def __init__(self,pluginMgr,serviceMgr):
        self.pluginMgr = pluginMgr
        self.serviceMgr = serviceMgr
        self.require = self.requirePlugin
    def requirePlugin(self,name):
        if name not in self.pluginMgr.plugins:
            self.pluginMgr.load_plugin(name)
        return self.pluginMgr.get_plugin(name)
    def requireService(self,cname):
        # TODO: add automatic service finder
        if name not in self.serviceMgr.all_services:
            raise NotImplementedError("Service %s could not be found!"%cname)

class SharedStorage():
    def __init__(self,name):
        self.data = {}
        self.default = -1
        self.name = name
    def __getattr__(self,key):
        if key not in ["data","default","name"]:
            try:return self.data[key]
            except Exception:
                if self.default == -1:
                    raise AttributeError("SharedStorage does not contain key %s"%key)
                else:
                    return self.default
        elif key in ["data","default","name"]:
            return self.__dict__[key]
    def __getitem__(self,key):
        return self.__getattr__(key)
    def __setattr__(self,key,value):
        if key in ["data","default","name"]:
            self.__dict__[key]=value
        else:
            self.data[key]=value
    def __setitem__(self,key,value):
        self.__setattr__(key,value)

class Manager():
    def __init__(self,include=[]):
        self.included = include
        self.data = {}
    def __getattr__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self.data and not key.startswith("_"):
            return self.data[key]
        else:
            for s in self.included:
                if key in s.__dict__ and not key.startswith("_"):
                    return s.__dict__[key]
            raise KeyError("Key %s does not exist in Manager at %s"%(key,hex(id(self))))
    def __getitem__(self,key):
        return self.__getattr__(key)
    def __setitem__(self,key,value):
        self.data[key] = value
    # Not needed, add_service will automagically become available through __getattr__, but only if a ServiceManager or similiar already exists.
    # Uncomment to overwrite service adding methods to automatically add a ServiceManager if one doesn't exist.
    #def add_service(self,*args,**kwargs):
    #    serviceMgr = None
    #    for s in self.included:
    #        if isinstance(s,core.ServiceManager):
    #            serviceMgr = s
    #    if serviceMgr == None:
    #        serviceMgr = core.ServiceManager()
    #    serviceMgr.add_service(*args,**kwargs)

class LogManager():
    pass
