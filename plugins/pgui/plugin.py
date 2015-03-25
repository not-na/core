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
import pygame
pygame.init()

import pgui

shs = core.gvar

class GuiApplication(core.Application):
    def __init__(self,name):
        core.Application.__init__(self,name)
        self._globevhandlers = [self._menuevhandler]
        self._evhandlers = {pygame.KEYDOWN:[self._keyhandler],pygame.MOUSEBUTTONDOWN:[self._clickhandler],pygame.QUIT:[self.stop]}
        self._keyhandlers = [self._keystrokehandler]
        self._keystrokes = {}
        self.menu = pgui.MenuManager()
    def add_evhandler(self,evid,handler):
        if evid not in self._evhandlers:
            self._evhandlers[evid]=[]
        self._evhandlers[evid].append(handler)
    def add_clickhandler(self,handler):
        self._keyhandlers.append(handler)
    def handle_event(self,e):
        if e.type in self._evhandlers:
            for h in self._evhandlers[e.type]:
                try:
                    h(e)
                except Exception:
                    print("[pgui] Eventhandler for event %s raised Exception!"%e.type)
    def draw(self):
        return self.menu.draw()
    def do_single_loop(self):
        events = pygame.event.get()
        for e in events:
            self.handle_event(e)
        self.screen.blit(self.draw(),[0,0])
        pygame.display.flip()
    def set_display(self,size,flags=None):
        if flags == None:
            self.screen = pygame.display.set_mode(size)
        elif flags != None:
            self.screen = pygame.display.set_mode(size,flags)
        self.menu.set_size(size)
    def getOptimalDisplaySize(self):
        return [1000,500] # TODO: add real optimal screen size function
    def setFontName(self,name="Arial"):
        pgui.init(pygame.font.Font(name,20,False,False))
    def add_keystroke(self,key,shift=False,ctrl=False,alt=False,meta=False,caps=False,num=False):
        kmod = 0
        if shift:kmod = kmod|pygame.KMOD_SHIFT
        if ctrl:kmod = kmod|pygame.KMOD_CTRL
        if alt:kmod = kmod|pygame.KMOD_ALT
        if meta:kmod = kmod|pygame.KMOD_META
        if caps:kmod = kmod|pygame.KMOD_CAPS
        if num:kmod = kmod|pygame.KMOD_NUM
        self._keystrokes[[key,kmod]]
    def _clickhandler(self,e):
        pass
    def _menuevhandler(self,e):
        self.menu.handle_event(e)
    def _keyhandler(self,e):
        for f in self._keyhandlers:
            try:
                f(e)
            except Exception:
                print("[pgui] Keyhandler for key %s raised error while calling"%pygame.key.name(e.key))
    def _keystrokehandler(self,e):
        kmod = pygame.key.get_mods()
        key = e.key
        l = [key,kmod]
        if l in self._keystrokes:
            try:
                self._keystrokes[l](e)
            except Exception:
                print("[pgui] Keystroke handler for keystroke %s raised Exception"%l)

BaseMenu = pgui.BaseMenu
Menu = pgui.Menu

Widget = pgui.Widget
MovableWidgetContainer = pgui.MovableWidgetContainer
CheckBox = pgui.CheckBox
Button = pgui.Button
TextBox = pgui.TextBox
PasswordBox = pgui.PasswordBox
MultiLineTextBox = pgui.MultiLineTextBox
ScrollableTextView = pgui.ScrollableTextView
DropDownSelector = pgui.DropDownSelector
SubWidget = pgui.SubWidget
DropDownMenuEntry = pgui.DropDownMenuEntry
IconDropDownMenuEntry = pgui.IconDropDownMenuEntry
StaticText = pgui.StaticText


