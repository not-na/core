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
shs = core.gvar

import pyglet
from pyglet.gl import *

_keys = pyglet.window.key
_mouse = pyglet.window.mouse

win = pyglet.window.Window()

@win.event
def on_draw():
    app._evdraw()
@win.event
def on_key_press(k,kmod):
    app._evkeypress(k,kmod)
@win.event
def on_mouse_press(x,y,button,modifiers):
    app._evmousepress([x,y],button,modifiers)

def normalizePos2(pos,sizey=None):
    """Converts from coordinates relative to the lower-left corner to coordinates relative to the uper-left corner."""
    if sizey == None:
        sizey = app.size2[1]
    return [pos[0],sizey-pos[1]]

class Shape():
    def __init__(self,size):
        self.size = size
    def getVertices(self,pos):
        pass
    def draw(self,pos):
        pass

class ShapeCube():
    def __init__(self,size):
        self.size = size
    def getVertices(self,pos):
        n = self.size
        x = pos[0]
        y = pos[1]
        z = pos[2]
        return [
                x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n, # top
                x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n, # bottom
                x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n, # left
                x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n, # right
                x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n, # front
                x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n, # back
                ]

class ShapeTriangle():
    def __init__(self,size):
        self.size = size
    def getVertices(self,pos):
        x = pos[0]
        y = pos[1]
        z = pos[2]
        sx = self.size[0]
        sy = self.size[1]
        sz = self.size[2]
        return [
                x,x+sx, y,y+sy, z,z+sz
        ]
    def draw(self,pos):
        v = self.getVertices(pos)
        glDrawArrays(GL_TRIANGLES, 0, len(v) // 2)

class ShapeContainer():
    def __init__(self,shape):
        self.shape = shape
        self.poses = []
    def draw(self):
        for p in self.poses:
            self.shape.draw(p)
    def addPos(self,pos):
        self.poses.append(pos)

class PygletApplication(core.Application):
    def __init__(self,name,debug=False):
        global app
        core.Application.__init__(name)
        self.win = win
        app = self
        self.size2 = [0,0]
        self.size3 = [0,0,0]
        self.imgs = {}
        if debug:
            self._debug()
    def setFontName(self,name="Arial"):
        pass
    def loadImg(self,fname,name=None):
        img = pyglet.resource.image(fname)
        if name == None:
            self.imgs[fname]=img
        else:
            self.imgs[name]=img
        return img
    def run_single_loop(self):
        raise NotImplementedError("You can't run a single loop of an OpenGL app.")
    def run_forever(self):
        pyglet.app.run()
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        for obj in self.objects:
            o = self.objects[obj]
            if o.visible:
                o.draw()
    def _debug(self):
        window.push_handlers(pyglet.window.event.WindowEventLogger())
    def _evdraw(self):
        pass
    def _evkeypress(self,k,kmod):
        pass
    def _evmousepress(self,pos,button,modifiers):
        pass
