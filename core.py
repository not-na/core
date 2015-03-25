#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  core.py
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
import sys,os,collections,imp

try:
    import threading
    THREADING_AVAIL = True
except ImportError:
    print("core: Threading module couldn't be loaded, async events will not be available.")
    print("core: Async Events will be automatically threat like normal events.")
    THREADING_AVAIL = False

# core.py is a extensible framework for applications
# all classes are just base classes, if you want to add more features you just need to subclass the classes, however you should be fine using the baseclasses for most purposes

class CoreError(Exception):pass # used for most core-related exceptions

class Application():
    def __init__(self,name):
        """Basic application with the name `name`.
        To start an Application you need to do app.run_forever(), and to stop an Application you need to call app.stop()"""
        self.name = name
        self.running = False
    def do_single_loop(self):
        """Does a single loop of the Application.
        Must be overwritten by subclasses, does nothing by default.
        This is where all your event-handling, rendering and logic goes."""
        pass
    def run_forever(self):
        """Calls app.do_single_loop as long as app.running is true.
        If you want to add event-handling, rendering or logic, add it to do_single_loop, not here.
        This uses a while loop, so to exit the app, you must set either app.running to false by calling app.stop() or press CTRL+C."""
        self.running = True
        while self.running:
            self.do_single_loop()
    def stop(self):
        """Simplay stopps the application if running.
        This uses app.running.
        If you want to implement custom stopping behaviour, such as closing files and/or saving data to disk, implement it here."""
        self.running = False
    def __del__(self):
        """Just a basic function that should get called when the programm exits, just automatically calls app.stop()"""
        self.stop()

class PluginManager():
    def __init__(self,searchpaths=["./","./plugins","./addons"]):
        """Basic extensible plugin manager.
        This class is not responsible for providing API functions, it just loads and caches plugins.
        The plugin manager is initialized with some searchpaths, the searchpaths default to the current directory plus the directorys
        ./plugins and ./addons, if a plugin is loaded, these paths are scanned for valid plugins.
        You can modify the searchpaths by either the parameter searchpaths as a list or via the instance attribute PluginManager.searchpaths."""
        self.searchpaths = searchpaths
        self.plugins = {}#collections.OrderedDict()
        self.finders = []
        self.addFinder(Finder()) # just adds the default plugin finder for convenience
    def load_plugin(self,name,add_searchpaths=[]):
        """This function loads the plugin `name` into the internal cache with the (optional) additional searchpaths `add_searchpaths`.
        In order to load a plugin, first all the searchpaths are scanned using the registered finders and then the plugin is loaded using the plugin's load() method.
        It also checks if the plugin is loaded, if it is, nothing is done.
        For convenience, the loaded plugin will be returned."""
        sp = self.searchpaths[:]
        sp.extend(add_searchpaths)
        if name in self.plugins:
            return self.plugins[name]
        r2 = None
        for f in self.finders:
            r = f.find(sp,name)
            if r[0]==True:
                r2 = r[1]
                r2.load()
        if r2 == None:
            raise NameError("Plugin %s can't be found."%name)
        self.plugins[name]=r2
        return r2
    def get_plugin(self,name):
        """Returns the plugin named `name` from the internal cache.
        If the plugin is not found, an exception is raised."""
        if name in self.plugins:
            return self.plugins[name]
        else:
            raise NameError("plugin %s is not loaded"%name)
    def publishToAll(self,key,value):
        """This is a convenience function that sets the attribute `key` on all plugins to be `value`.
        It is not recommended to use this function because it has various security and compatability implications."""
        for p in self.plugins:
            p.__setattr__(key,value)
    def addFinder(self,finder):
        """Use this to add finder instances to the PluginManager.
        Finders are used in load_plugin to locate a plugin.
        See core.Finder for an example Finder Class.
        """
        self.finders.append(finder)

class Finder():
    def __init__(self):
        """A basic plugin Finder class.
        This class implements the default behaviour of plugin loading and is always available.
        For this Finder, a valid plugin consists of a directory of the plugins name containing a file called plugin.py,
        that file is then loaded using python's imp module and the resulting module object is used as the plugin.
        By default, this loads plugins using the core.Plugin class, this is not easily changeable because this Finder is tightly integrated with the core.Plugin class."""
        pass
    def find(self,searchpath,name):
        """Finds a valid plugin in the searchpaths `searchpath` with the name `name`.
        For more details, see the docs in the __init__ func."""
        r=[False,None]
        for s in searchpath:
            r = self._recfind(s,name)
            if r[0]:
                break
        if not r[0]:
            return [False,None]
        elif r[0]:
            return [True,Plugin(r[1],name)]
    def _recfind(self,s,name):
        """Internal method used to recursively parse directorys, crawling them for a plugin named `name`.
        This method is intended for internal use only."""
        for p in os.listdir(s):
            if p==name and os.path.isdir(os.path.join(s,p)):
                return [True,os.path.join(s,p,"plugin")]
            elif os.path.isdir(os.path.join(s,p)):
                r = self._recfind(os.path.join(s,p),name)
                if r[0]:
                    return r
        return [False,None]

class Plugin():
    def __init__(self,fpath,name):
        """Class representing a simple plugin with the name `name`.
        The plugin will be loaded from file `fpath` which should be a valid python source file ending with .py, the ending should not be included in the filename.
        This class was designed for the Finder class core.Finder and may not work when used with other finders.
        The plugin is not automatically loaded, you need to call plugin.load() to actually load the plugin."""
        self.fpath = fpath
        self.name = name
    def load(self):
        """Loads the plugin.
        This uses the parameters given when instantiating.
        The resulting module object will be stored in the internal variable plugin._m.
        All the module's content will be assigned to the plugin instance, this allows the plugin to overwrite special attributes like __getattr__ or __del__."""
        f = open(self.fpath+".py","r")
        m = imp.load_module(self.name,f,self.fpath+".py",[".py","r",imp.PY_SOURCE])
        self._m = m
        self.__dict__.update(m.__dict__)

class Service():
    def __init__(self,cid,name,cls):
        """Class representing a base service.
        A service consists of a general id `cid`, a name `name` and the corresponding class/function `cls`.
        The name should be unique across all services and usually is the class/function name including the package.
        A general ID is mainly used to address services, eg. if you request a service, you request it by its general ID.
        The general ID must not be unique.
        If a service is requested, the corresponding function/class is instantiated/called.
        For convenience, when the service object is called, it acts the same as if it would have been requested."""
        self.cid = cid
        self.name = name
        self.cls = cls
    def onrequestservice(self,*args,**kwargs):
        """Requests the service.
        If the service is a function, this calls the function using the given parameters.
        If the service is a class, this instantiates the class using the given parameters."""
        return self.cls(*args,**kwargs)
    def __call__(self,*args,**kwargs):
        """Convenience function allowing to automatically instantiate the service when it's called."""
        return self.onrequestservice(*args,**kwargs)

class ServiceManager():
    def __init__(self):
        self.services = {}
        self.all_services = {}
    def add_service(self,service):
        if service.cid not in self.services:
            self.services[service.cid]=[]
        self.services[service.cid].append(service)
        self.all_services[service.cid]=service
    def get_service(self,cid):
        return self.services[cid]
    def service(self,cid):
        return self.services[cid][0]

class Event():
    def __init__(self,etype,target,data={}):
        self.etype = etype
        self.target = target
        self.data = data
        self.handled = False
    def stopProccessing(self):
        self.handled = True
    def shouldProcess(self):
        return not self.handled
    def __repr__(self):
        return "<core.Event instance at %s of type %s with data %s>"%(hex(id(self)),self.etype,self.data)

class EventManager():
    def __init__(self):
        self.async_queue = []
        self.handlers = {}
        self.evhandlers = {}
        self.processing = False
        if THREADING_AVAIL:
            self._process_thread = threading.Thread(target=self._process)
    def push(self,event,async=False):
        if isinstance(event,dict):
            event = Event(event["etype"],event["target"],event)
        target = event.target
        if async == False or not THREADING_AVAIL: # if threading is not available, process as normal
            if target in self.handlers:
                for h in self.handlers[target]:
                    h(event)
                    if not event.shouldProcess():
                        break
            if event.etype in self.evhandlers:
                for h in self.evhandlers[event.etype]:
                    h(event)
                    if not event.shouldProcess():
                        break
        elif async == True:
            self.async_queue.append(event)
            self.start_processing_events()
    def add_event_handler(self,event,handler):
        if event not in self.evhandlers:
            self.evhandlers[event]=[]
        self.evhandlers[event].append(handler)
    def add_handler(self,target,handler):
        if target not in self.handlers:
            self.handlers[target]=[]
        self.handlers[target].append(handler)
    def del_handler(self,target,handler):
        if target not in self.handlers:
            raise NameError("Event handler %s could not be found for target %s"%(handler,target))
        if handler not in self.handlers[target]:
            raise NameError("Event handler %s could not be found for target %s"%(handler,target))
        del self.handlers[target][handler]
    def start_processing_events(self):
        if not THREADING_AVAIL:
            raise CoreError("Can't process async events when threading is not available!")
        if self.processing:
            return
        self.processing = True
        self._process_thread.run()
    def emit(self,etype,target,data={},async=False):
        """Shorthand for push(Event(etype,target,data),async)."""
        return self.push(Event(etype,target,data),async)
    def _process(self):
        q = self.async_queue[:] # cloned to avoid losing of events while processing
        for event in q:
            self.push(event,False)
        del self.async_queue[0:len(q)-1]
        self._process_thread = threading.Thread(target=self._process)
        self.processing = False
    

gvar = None # gvar can be used to share information between plugins, makes information exchange a lot easier
# It is recommended to use a dictionary or a SharedStorage object from core_essentials

if __name__ == '__main__':
    # adds an debug option if core.py itself is started AND the parameters are EXACTLY --core-dev-debug=True; this includes the file name/path and the exact spelling
    # maybe add something to prevent that anybody could use this to cheat, something like checking for the presence of the devel librarys of python, just so the average cheater would get blocked
    if sys.argv == ["core.py","--core-dev-debug=True"]:
        print("debugging activated")
        DEBUG = True
    print("You can not run core itself, you must launch the appropriate application.")
    # tries to execute different common used filenames in the current directory, just for convenience, do not rely on this
    if os.path.exists("main.py"):
        print("trying to run the file main.py in current directory")
        os.system("python main.py")
    elif os.path.exists("app.py"):
        print("trying to run the file app.py in current directory")
        os.system("python app.py")
    elif os.path.exists("application.py"):
        print("trying to run the file application.py in current directory")
        os.system("python application.py")
    else:
        print("couldn't find any common used filenames to start, exiting")
        sys.exit(1) # exit with a status of 1 to indicate that something went wrong
