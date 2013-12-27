#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	  pybluetoothserial.py (PBS) : Connect to bluetooth serial devices.
	
	           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004
 
	Copyright (C) 2013 Thomas Maurice <tmaurice59@gmail.com>
	 
	Everyone is permitted to copy and distribute verbatim or modified
	copies of this license document, and changing it is allowed as long
	as the name is changed.
	 
		         DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
		TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
	 
	 0. You just DO WHAT THE FUCK YOU WANT TO.
	 
"""

__author__ = "Thomas Maurice"
__copyright__ = "Copyright 2013, Thomas Maurice"
__license__ = "WTFPL"
__version__ = "0.1"
__maintainer__ = "Thomas Maurice"
__email__ = "tmaurice59@gmail.com"
__status__ = "Development"

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import math
import time
import pango
import bluetooth as bluez
import sys
import select
import threading
import string

class MainWindow:
	def __init__(self):
		"""
			Initialization of the software's main window
		"""
		self.init_window()
		self.init_layouts()
		self.init_mode()
		self.init_textview()
		self.init_sendBar()
		self.init_searchBar()
		
		# some constants
		self.HEXMODE = 0
		self.ASCIIMODE = 1
		self.BOTHMODE = 2
		
		self.searchThread = None
		self.socket = None
		self.services = None
		self.connected = False
		self.hexcount = 0
		self.mode = self.BOTHMODE
		
		# Main window signals
		self.window.connect("destroy", self.exitProgram)
		
		# Show all
		self.mainLayout.pack_start(self.scrolledWindow, gtk.FILL|gtk.EXPAND)
		self.mainLayout.pack_start(self.sendBarLayout, gtk.SHRINK)
		self.mainLayout.pack_start(self.modeLayout, gtk.SHRINK)
		self.mainLayout.pack_start(self.searchLayout, gtk.SHRINK)
		self.window.add(self.mainLayout)
		self.window.show_all()
		
		self.window.set_focus(self.textEntry)
		
		gobject.timeout_add(100, self.recieveSerial)
		gobject.timeout_add(500, self.refreshInterface)
		gobject.threads_init()
		
		self.textBuffer.set_text(">>           Welcome in pybluetoothserial.py (PBS)\n")
		self.textBuffer.insert(self.textBuffer.get_end_iter(), ">>                  v0.1 by Thomas Maurice\n\n")
		
		
		self.searchThread = threading.Thread(target=self.searchDevices)
		self.searchThread.start()
	
	def textViewChanged(self, widget, event, data=None):
		"""
			This will automatically scroll the textview to the end
		"""
		adj = self.scrolledWindow.get_vadjustment()
		adj.set_value(adj.upper - adj.page_size)
	
	def refreshInterface(self):
		"""
			Will refresh the interface, setting unactivated/activated
			everything that must be
		"""
		if self.searchThread.isAlive() == True or self.connected == True:
				self.searchButton.set_sensitive(False)
		
		else:
			self.searchButton.set_sensitive(True)
	
	def modeChanged(self, data=None):
		if self.hexButton.get_active() == True:
			self.mode = self.HEXMODE
		elif self.asciiButton.get_active() == True:
			self.mode = self.ASCIIMODE
		else:
			self.mode = self.BOTHMODE
	
	def clearBuffer(self, data=None):
		self.textBuffer.set_text("")
		self.hexcount = 0
		
	def init_textview(self):
		"""
			Initializes the text view
		"""
		self.textView = gtk.TextView()
		self.textView.set_editable(False)
		fontdesc = pango.FontDescription("monospace 10")
		self.textView.modify_font(fontdesc)
		self.textBuffer = self.textView.get_buffer()
		self.scrolledWindow = gtk.ScrolledWindow()
		self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		self.scrolledWindow.add_with_viewport(self.textView)
		self.scrolledWindow.set_size_request(-1, 300)
		self.textView.connect('size-allocate', self.textViewChanged)
	
	def init_layouts(self):
		"""
			Layouts !
		"""
		self.modeLayout = gtk.HBox()
		self.searchLayout = gtk.HBox()
		self.mainLayout = gtk.VBox()
		self.sendBarLayout = gtk.HBox()
	
	def init_mode(self):
		self.hexButton = gtk.RadioButton(label="Hex display")
		self.hexButton.set_active(False)
		self.asciiButton = gtk.RadioButton(label="ASCII display", group=self.hexButton)
		self.asciiButton.set_active(True)
		self.bothButton = gtk.RadioButton(label="Both (ASCII+Hex)", group=self.hexButton)
		self.bothButton.set_active(True)
		self.modeLayout.pack_start(self.hexButton, gtk.SHRINK)
		self.modeLayout.pack_start(self.asciiButton, gtk.SHRINK)
		self.modeLayout.pack_start(self.bothButton, gtk.SHRINK)
		self.hexButton.connect("clicked", self.modeChanged)
		self.asciiButton.connect("clicked", self.modeChanged)
		self.bothButton.connect("clicked", self.modeChanged)
	
	def init_window(self):
		"""
			Initialization of the main window
		"""
		self.window = gtk.Window()
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_default_size(480, 100)
	
	def init_sendBar(self):
		"""
			Initializes the send bar
		"""
		self.textEntry = gtk.Entry()
		self.textEntry.set_can_focus(True)
		self.sendButton = gtk.Button("Send")
		self.clearButton = gtk.Button("Clear")
		
		self.textEntry.connect("activate", self.serialSend)
		self.sendButton.connect("clicked", self.serialSend)
		self.clearButton.connect("clicked", self.clearBuffer)
		
		self.sendBarLayout.pack_start(self.textEntry, gtk.SHRINK)
		self.sendBarLayout.pack_start(self.sendButton, gtk.SHRINK)
		self.sendBarLayout.pack_start(self.clearButton, gtk.SHRINK)
	
	def init_searchBar(self):
		"""
			Initializes the search bar
		"""
		self.devicesList = gtk.combo_box_new_text()
		self.searchSpinner = gtk.Spinner()
		self.searchButton = gtk.Button("Scan", gtk.STOCK_REFRESH)
		self.connectButton = gtk.Button("Connect")
		self.searchButton.connect("clicked", self.asyncSearchDevices)
		self.connectButton.connect("clicked", self.connectToDevice)
		self.searchLayout.pack_start(self.devicesList, gtk.SHRINK)
		self.searchLayout.pack_start(self.searchButton, gtk.SHRINK)
		self.searchLayout.pack_start(self.connectButton, gtk.SHRINK)
		self.searchLayout.pack_start(self.searchSpinner, gtk.SHRINK)
		
		self.connectButton.set_sensitive(False)
	
	def recieveSerial(self, data=None):
		if self.connected:
			r, _, _ = select.select([self.socket], [], [], 0)
			if r != []:
				s = self.socket.recv(1024)
				if self.mode == self.HEXMODE or self.mode == self.BOTHMODE:
					for c in s:
						h = '['+hex(ord(c))
						if len(h) < 5:
							h += " "
						if self.mode == self.BOTHMODE:
							h += " "
							if self.isCharPrintable(c) == True:
								h += c
							else:
								h += "."
						h += "]"
						self.textBuffer.insert(self.textBuffer.get_end_iter(), h)
						self.hexcount+=1
						if self.hexcount >= 7:
							self.textBuffer.insert(self.textBuffer.get_end_iter(), "\n")
							self.hexcount = 0
				else:
					self.textBuffer.insert(self.textBuffer.get_end_iter(), s)
		return True
	
	def isCharPrintable(self, c):
		if  (c in string.letters) or (c in string.digits) or (c in (string.punctuation+" ")):
			return True
		else:
			return False
	
	def serialSend(self, data=None):
		"""
			Send data to the connected port
		"""
		if self.textEntry.get_text() == "":
			return
		
		if self.connected == True:
			print ">", self.textEntry.get_text()
			if self.socket.send(self.textEntry.get_text()) < 0:
				print "Error sending message :("
				self.textBuffer.insert(self.textBuffer.get_end_iter(), "\n>> Error sending message, closing connexion\n")
				self.socket.close()
				self.connectButton.set_label("Connect")
				self.connected = False

		self.textEntry.set_text("")
	
	def connectToDevice(self, data=None):
		"""
			Connect the computer to a serial device
		"""
		if self.connected == True:
			self.socket.close()
			self.connectButton.set_label("Connect")
			self.connected = False
			self.textBuffer.insert(self.textBuffer.get_end_iter(), "\n>> Disconnected from host\n")
			return
			
		self.socket = bluez.BluetoothSocket(bluez.RFCOMM)
		for s in self.services:
			if s["name"] == self.devicesList.get_active_text():
				try:
					self.textBuffer.insert(self.textBuffer.get_end_iter(), "\n>> Connecting to "+s["host"]+"... ")
					self.socket.connect((s["host"], s["port"]))
					self.connectButton.set_label("Disconnect")
					self.connected = True
					self.hexcount = 0
					self.textBuffer.insert(self.textBuffer.get_end_iter(), "[ OK ]\n")
				except Exception as e:
					print "Error, unable to connect ! ", e.message[1]
					self.connected = False
					self.connectButton.set_label("Connect")
					self.textBuffer.insert(self.textBuffer.get_end_iter(), "[FAIL]\n")

	def asyncSearchDevices(self, data=None):
		"""
			Asynchronously launches the search thread
			
			If a previous instance of the search thread is launched
			then it will be closed to make room for the new one
		"""
		if self.searchThread.isAlive():
			self.searchThread._Thread__stop()
			
		self.searchThread = threading.Thread(target=self.searchDevices)
		self.searchThread.start()
	
	def searchDevices(self):
		"""
			Search for devices
		"""
		self.searchButton.set_sensitive(False)
		print "Scanning for devices..."
		while self.devicesList.get_active() != -1:
			self.devicesList.remove_text(0)
			
		self.textBuffer.insert(self.textBuffer.get_end_iter(), ">> Searching Bluetooth serial ports... ")
		self.searchSpinner.start()
		self.searchSpinner.show()
		try:
			self.services = bluez.find_service(uuid=bluez.SERIAL_PORT_CLASS)
		except Exception as e:
			print "Error, unable to search devices :", e.message[1]
			return

		self.textBuffer.insert(self.textBuffer.get_end_iter(), "found " + str(len(self.services)) + "\n")
		for i in range (len(self.services)):
			print " -> Found", self.services[i]["name"], "at", self.services[i]["host"]
			self.textBuffer.insert(self.textBuffer.get_end_iter(),
				" -> " + self.services[i]["name"] +
				" (" + bluez.lookup_name(self.services[i]["host"], 3)+ ") at " +
				self.services[i]["host"])
			self.devicesList.append_text(self.services[i]["name"])
			self.devicesList.set_active(0)
				

		self.searchSpinner.stop()
		self.searchSpinner.hide()
		self.searchButton.set_sensitive(True)
		if len(self.services) > 0:
			self.connectButton.set_sensitive(True)
	
	def exitProgram(self, data=None):
		try:
			self.socket.close()
		except:
			pass # pas grave
		self.searchThread._Thread__stop()
		gtk.main_quit()
	
	def main(self):
		"""
			Sofwtware's main loop
		"""
		gtk.main()

if __name__ == "__main__":
	w = MainWindow()
	try:
		w.main()
	except KeyboardInterrupt:
		w.window.destroy()
		print "Exited by user"
