#   Copyright (C) 2021, 2022, 2023 Anirban Banerjee
#   
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/python3
import evdev
import sys
from time import sleep
import subprocess
import tkinter as tk
import tkinter.simpledialog
import tkinter.messagebox
import threading
import pexpect
from select import select

DEBUG1 = 0
DEBUG2 = 0
DEBUG3 = 0
DEBUG4 = 0
DEBUG5 = 1

def dbg1print (*argv, testCondition=True):
	try:
		if testCondition == False:
			return
		if DEBUG1 != 0:
			for arg in argv:
				print (arg, end='')
			print ('')
	except:
		pass

def dbg2print (*argv):
	try:
		if DEBUG2 != 0:
			for arg in argv:
				print (arg, end='')
			print ('')
	except:
		pass

def dbg3print (*argv):
	try:
		if DEBUG3 != 0:
			for arg in argv:
				print (arg, end='')
			print ('')
	except:
		pass

def dbg4print (*argv, testCondition=True):
	try:
		if testCondition == False:
			return
		if DEBUG4 != 0:
			for arg in argv:
				print (arg, end='')
			print ('')
	except:
		pass

def dbg5print (*argv):
	try:
		if DEBUG5 != 0:
			for arg in argv:
				print (arg, end='')
			print ('')
	except:
		pass

MOVEMENT_KEYLIST = [
	evdev.ecodes.BTN_LEFT,
	evdev.ecodes.BTN_RIGHT,
	evdev.ecodes.BTN_MIDDLE,
	evdev.ecodes.KEY_DELETE,
	evdev.ecodes.KEY_BACKSPACE,
	evdev.ecodes.KEY_TAB,
	evdev.ecodes.KEY_ENTER,
	evdev.ecodes.KEY_SPACE,
	evdev.ecodes.KEY_HOME,
	evdev.ecodes.KEY_END,
	evdev.ecodes.KEY_PAGEUP,
	evdev.ecodes.KEY_PAGEDOWN,
	evdev.ecodes.KEY_UP,
	evdev.ecodes.KEY_DOWN,
	evdev.ecodes.KEY_LEFT,
	evdev.ecodes.KEY_RIGHT
]

NOREMAP_KEYLIST = [
	evdev.ecodes.BTN_LEFT,
	evdev.ecodes.BTN_RIGHT,
	evdev.ecodes.BTN_MIDDLE,
	evdev.ecodes.KEY_ESC,
	evdev.ecodes.KEY_BACKSPACE,
	evdev.ecodes.KEY_DELETE,
	evdev.ecodes.KEY_TAB,
	evdev.ecodes.KEY_ENTER,
	evdev.ecodes.KEY_LEFTCTRL,
	evdev.ecodes.KEY_LEFTSHIFT,
	evdev.ecodes.KEY_RIGHTSHIFT,
	evdev.ecodes.KEY_KPASTERISK,
	evdev.ecodes.KEY_LEFTALT,
	evdev.ecodes.KEY_SPACE,
	evdev.ecodes.KEY_CAPSLOCK,
	evdev.ecodes.KEY_ESC,
	evdev.ecodes.KEY_BACKSPACE,
	evdev.ecodes.KEY_HOME,
	evdev.ecodes.KEY_END,
	evdev.ecodes.KEY_PAGEUP,
	evdev.ecodes.KEY_PAGEDOWN,
	evdev.ecodes.KEY_UP,
	evdev.ecodes.KEY_DOWN,
	evdev.ecodes.KEY_LEFT,
	evdev.ecodes.KEY_RIGHT
]

class wordState():

	def __init__(self, kbd="dev"):

		self.firstVowel = ''
		self.charmap1 = {}
		self.charmap2 = {}
		self.varna = {}
		self.kc1 = {}
		self.kc2 = {}
		fileDone = self.parseKeycodefile("keycode.map")
		if kbd == "dev":
			fileDone = self.parseMapfile("d.map")
		elif kbd == "ben":
			fileDone = self.parseMapfile("b.map")

	def parseKeycodefile (self, filename=None):
		retVal = True
		#print ("parseKeycodefile: filename is ...", filename)
		#print ("parseKeycodefile: opening file filename is ...", filename)
		try:
			with open(filename, "r") as f:
				for line in f:
					#print (line)
					keycode, ascii1, ascii2 = '_', '_', '_'
					#find the comment character ##
					commentFoundPos = line.find('##')
					if commentFoundPos == 0:
						continue
					else:
						line = line[ : commentFoundPos].strip()
					if line == '':
						continue
					lineList = line.split()
					#print (lineList)
					#discard comments
					if len(lineList) >= 2:
						keycode, ascii1, ascii2 = lineList 
						#print ("key is ---", key)
					else:
						print('Warning: Illegal Keycode File')
						print (lineList)
						retVal = False
						break
					self.charmap1[int(keycode)] = ascii1
					self.charmap2[int(keycode)] = ascii2
		except FileNotFoundError:
			print ("Error: Map file "+filename+" was not found.", caption="Keycode File Error")
			retVal = False

		#for i in self.charmap1.keys():
			#print (i, " -> ", self.charmap1[i])
		return retVal

	def parseMapfile (self, filename=None, dontErasePreviousMaps=False):
		#do not clear reverse and ucode dicts
		#as these might be needed for mixed texts
		if dontErasePreviousMaps == False:
			self.varna.clear()
			self.kc1.clear()
			self.kc2.clear()
			self.firstVowel = ''

		retVal = True
		#print ("parseMapfile: filename is ...", filename)
		#print ("parseMapfile: opening file filename is ...", filename)
		try:
			with open(filename, "r") as f:
				for line in f:
					#print (line)
					key, v, _, kc1, _, kc2 = '_', '_', '_', '_', '_', '_'
					#find the comment character ##
					commentFoundPos = line.find('##')
					if commentFoundPos == 0:
						continue
					else:
						line = line[ : commentFoundPos].strip()
					if line == '':
						continue
					lineList = line.split()
					#print (lineList)
					#discard comments
					if len(lineList) == 6:
						key, v, _, kc1, _, kc2 = lineList 
						#print ("key is ---", key)
					else:
						print('Warning: Illegal Map File')
						print (lineList)
						retVal = False
						break
						
					self.kc1[key] = []
					if kc1 != '_':
						self.kc1[key] += kc1.split('+')
					
					self.varna[key] = v.upper()
					self.kc2[key] = []
					if kc2 != '_' and ('VOWEL' == self.varna[key] or 'MODIFIER' == self.varna[key]):
						self.kc2[key] = kc2.split('+')

					if self.varna[key] == "VOWEL" and self.kc2[key] == []:
						#first/default vowel is one that does not have the 2nd keycode/encoding
						self.firstVowel = key

					#print ("key -- values ", key, self.varna[key], self.kc1[key], self.kc2[key])
				#endfor
		except FileNotFoundError:
			print ("Error: Map file "+filename+" was not found.", caption="Map File Error")
			retVal = False

		self.VIRAMA = '32'
		self.ZWJ = 'SA57'
		self.ZWNJ = 'A57'

		#for i in self.kc1.keys():
			#print (i, " -> ", self.kc1[i], end='')
			#print (" -> ", self.kc2[i])
		return retVal

class remapper():
	def __init__(self, keyboardID = 'keyboard', mouseID = 'mouse', touchpadID = 'touchpad'):
		# Find all input devices.
		self.waitForSendKeysComplete = False
		self.consoleQuitFunction = None
		self.ioLoopQuitNow = False
		self.skipMapping = False
		self.translitScheme = "dev"
		self.loadDevanagari = True
		self.currentInputChar = ''
		self.bestMatchInputString = ''
		self.lastMatchType = ''
		self.lastMatchKeycodeList = []
		self.processState = "START"
		self.shiftStateEcode = 0
		self.shiftState = False #KEY_LEFTSHIFT or KEY_RIGHTSHIFT has been pressed
		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		# Limit the list to those containing keyboardID and pick the first one.
		self.keyboard = [d for d in devices if keyboardID in d.name.lower()][0]
		self.mouse = [d for d in devices if mouseID in d.name.lower()][0]
		self.touchpad = [d for d in devices if touchpadID in d.name.lower()][0]
		self.deviceDict = {self.keyboard.fd: self.keyboard, 
							self.mouse.fd: self.mouse, 
							self.touchpad.fd: self.touchpad}
		#self.inputdevices = {self.keyboard, self.mouse, self.touchpad}
		print ("mouse - ", self.mouse)
		print ("touchpad - ", self.touchpad)
		print ("keyboard - ", self.keyboard)
		try:
			self.keyboard.grab()  # Grab, i.e. prevent the keyboard from emitting original events.
		except:
			tk.messagebox.showerror(title="Error", message="Error: can't open the Evdev \nkeyboard device (/dev/uinput)")
			print("Error: can't open the Evdev device (/dev/input/*)")
			sys.exit(1)

		try:
			self.ui = evdev.UInput.from_device(self.keyboard, name='kbd')
		except:
			chmodsubproc = pexpect.spawn('sudo chmod +0666 /dev/uinput')
			passwd = tk.simpledialog.askstring("Password", "Enter password to enable writing into \nthe UInput device (/dev/uinput):", show='*')
			chmodsubproc.expect('\[sudo\] password for .*\: ')
			chmodsubproc.sendline(passwd)
			chmodsubproc.close()
			try:
				self.ui = evdev.UInput.from_device(self.keyboard, name='kbd')
			except:
				tk.messagebox.showerror(title="Error", message="Error: can't open the UInput device (/dev/uinput)")
				print("Error: can't open the UInput device (/dev/uinput)")
				sys.exit(1)
		# dummy initial write, else behaves like
		# https://github.com/gvalkov/python-evdev/issues/4
		# as if KEY_RETURN was kept pressed
		self.ui.write(evdev.ecodes.EV_KEY, 1, 1) #simulate escape press
		self.ui.syn()
		sleep(0.002)
		self.ui.write(evdev.ecodes.EV_KEY, 1, 0) #simulate escape  release
		self.ui.syn()
		sleep(0.002)
		self.ui.write(evdev.ecodes.EV_KEY, 14, 1) #simulate backspace press
		self.ui.syn()
		sleep(0.002)
		self.ui.write(evdev.ecodes.EV_KEY, 14, 0) #simulate backspace  release
		self.ui.syn()
		sleep(0.002)

		if self.skipMapping == False:
			self.loadXKB(self.translitScheme)
			self.wState = wordState(self.translitScheme)

	def loop(self):
		ui = self.ui
		#for event in self.keyboard.read_loop():  # Read events from original keyboard.
		while not self.ioLoopQuitNow:
			r, w, x = select(self.deviceDict, [], [])
			for fd in r:
				for event in self.deviceDict[fd].read():
					if self.waitForSendKeysComplete == True:
						#don't pass the event on
						continue
					if event.type == evdev.ecodes.EV_KEY:  # Process key and mouse events.
						#print ("event code = ", event.code, " = ", evdev.ecodes.KEY[event.code], " event value = ", event.value)
						if event.code == evdev.ecodes.KEY_ESC and event.value == 1 and event.type == 1: #check for the event.type, 1 is KEY
							# Exit on pressing Shift+ESC.
							#print ("loop: seeing ESCAPE self.shiftState is ", self.shiftState)
							if self.shiftState == True:
								self.consoleQuitFunction()
								self.ioLoopQuitNow = True
								break
							else:
								if event.value == 1:
									self.currentInputChar = ''
									self.bestMatchInputString = ''
									self.processState = "START"
									self.lastMatchKeycodeList = []
								ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
								ui.syn()
								sleep(0.002)
						elif event.code not in NOREMAP_KEYLIST and event.value == 1 and self.skipMapping == False and event.type == 1:
							#print ("ELIF not in NOREMAP_KEYLIST: event code = ", event.code, " = ", evdev.ecodes.KEY[event.code], " event value = ", event.value)
							#touchpad gestures register here -- we don't want these
							if fd == self.mouse.fd or fd == self.touchpad.fd:
								continue
							if event.code in self.wState.charmap1.keys():
								if self.shiftState == True:
									#print("keycode charmap1 = ", self.wState.charmap2[event.code])
									self.currentInputChar = self.wState.charmap2[event.code]
								else:
									#print("keycode charmap1 = ", self.wState.charmap1[event.code])
									self.currentInputChar = self.wState.charmap1[event.code]
							handled = self.map(self.currentInputChar, ui)
							if handled == False:
								#pass on unhandled events
								self.currentInputChar = ''
								self.bestMatchInputString = ''
								self.processState = "START"
								self.lastMatchKeycodeList = []
								ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
								ui.syn()
								sleep(0.002)
							while self.deviceDict[fd].read_one() != None:
								pass
							sleep(0.1) #sleep 100ms more
						elif event.code == evdev.ecodes.KEY_LEFTSHIFT or event.code == evdev.ecodes.KEY_RIGHTSHIFT and event.type == 1:
							self.shiftStateEcode = event.code
							self.shiftState = False
							if event.value == 1:
								self.shiftState = True
							#print ("loop: set self.shiftState to ", self.shiftState)
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value)
							ui.syn()
							sleep(0.002)
						elif event.value == 1 and event.code in MOVEMENT_KEYLIST:
							#print ("ELSE: event code = ", event.code, " = ", event.code, " event value = ", event.value, " event type = ", event.type)
							#for non-handled events like up/down/enter keys etc.
							#only for key presses, not key releases
							self.currentInputChar = ''
							self.bestMatchInputString = ''
							self.processState = "START"
							self.lastMatchKeycodeList = []
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
							ui.syn()
							sleep(0.002)
							while self.deviceDict[fd].read_one() != None:
								pass
							sleep(0.1) #sleep 100ms more
						else:
							# Passthrough other key events unmodified.
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
							ui.syn()
							sleep(0.002)
					else:
						#reset mapper variables when mouse clicks happen
						# Passthrough other events unmodified (e.g. SYNs).
						ui.write_event(event)

		#breaking out
		ui.write(evdev.ecodes.EV_KEY, 1, 0) #fake release ESCAPE
		sleep(0.002)
		ui.write(evdev.ecodes.EV_KEY, self.shiftStateEcode, 0) #pressed shift key release
		ui.syn()
		sleep(0.002)
		ui.close()

	def setConsoleQuitFunction(self, consoleQuitFunction):
		self.consoleQuitFunction = consoleQuitFunction

	def __exit__(self):
		try:
			print("UInput being closed...")
			self.ui.close()
			self.keyboard.ungrab()
			self.keyboard.close()
		except:
			print("EvDev/UInput already closed.")

	def loadXKB(self, kbd="dev"):
		subprocess.run(["/usr/bin/setxkbmap", kbd])

	def deletePrevious(self, count, ui):
		#print ("called deletePrevious for count = ", count)
		self.waitForSendKeysComplete = True
		for i in range(count):
			#print ("deleted 1...")
			ui.write(evdev.ecodes.EV_KEY, 14, 1) #backspace press
			self.ui.syn()
			sleep(0.002)
			ui.write(evdev.ecodes.EV_KEY, 14, 0) #backspace  release
			self.ui.syn()
			sleep(0.002)
		self.waitForSendKeysComplete = False

	def sendKeycodes(self, keycodeList, ui=None):
		print ("sendKeycodes: entered function -- keycodeList = ", keycodeList)
		self.waitForSendKeysComplete = True
		#return
		if self.shiftState == True:
			#SHIFT is already pressed, release 
			ui.write(evdev.ecodes.EV_KEY, self.shiftStateEcode, 0) #that shift key release
			ui.syn()
			sleep(0.002)

		for code in keycodeList:
			print ("keyCode = ", code)
			if code[0] == 'S':
				ui.write(evdev.ecodes.EV_KEY, 42, 1) #KEY_LEFTSHIFT press
				ui.syn()
				sleep(0.002)
				if code[1] == 'A':
					ui.write(evdev.ecodes.EV_KEY, 100, 1) #KEY_RIGHTALT press
					self.ui.syn()
					sleep(0.002)
					ui.write(evdev.ecodes.EV_KEY, int(code[2:]), 1)
					self.ui.syn()
					sleep(0.002)
					ui.write(evdev.ecodes.EV_KEY, int(code[2:]), 0)
					self.ui.syn()
					ui.write(evdev.ecodes.EV_KEY, 100, 0) #KEY_RIGHTALT release
					sleep(0.002)
				else:
					ui.write(evdev.ecodes.EV_KEY, int(code[1:]), 1)
					self.ui.syn()
					sleep(0.002)
					ui.write(evdev.ecodes.EV_KEY, int(code[1:]), 0)
					self.ui.syn()
					sleep(0.002)
				ui.write(evdev.ecodes.EV_KEY, 42, 0) #KEY_LEFTSHIFT release
				self.ui.syn()
				sleep(0.002)
			elif code[0] == 'A':
				ui.write(evdev.ecodes.EV_KEY, 100, 1) #KEY_RIGHTALT press
				self.ui.syn()
				sleep(0.002)
				ui.write(evdev.ecodes.EV_KEY, int(code[1:]), 1)
				self.ui.syn()
				sleep(0.002)
				ui.write(evdev.ecodes.EV_KEY, int(code[1:]), 0)
				self.ui.syn()
				sleep(0.002)
				ui.write(evdev.ecodes.EV_KEY, 100, 0) #KEY_RIGHTALT release
				self.ui.syn()
				sleep(0.002)
			else:
				ui.write(evdev.ecodes.EV_KEY, int(code), 1)
				self.ui.syn()
				sleep(0.002)
				ui.write(evdev.ecodes.EV_KEY, int(code), 0)
				self.ui.syn()
				sleep(0.002)
		if self.shiftState == True:
			#SHIFT is already pressed, release 
			ui.write(evdev.ecodes.EV_KEY, self.shiftStateEcode, 1) #that shift key press -- restore
			self.ui.syn()
			sleep(0.002)
		self.waitForSendKeysComplete = False

	def map(self, currentChar, ui=None):
		keycodeList = []
		currentWord = self.bestMatchInputString + currentChar
		matchContinuation = False
		matchFound = 0
		endIndex = 1
		bestMatchStr = ''
		print ("function map ----- currentWord is ", currentWord)
		dbg4print ("function map ----- len currentWord is ", len(currentWord))
		#print(currentWord[0:endIndex] in self.wState.kc1.keys())
		if currentWord in self.wState.kc1.keys():
			matchFound = 1
			bestMatchStr = currentWord
			matchContinuation = True
		elif currentChar in self.wState.kc1.keys():
			matchFound = 1
			bestMatchStr = currentChar

		if matchFound == 0:
			self.bestMatchInputString = ''
			self.processState = "START"
			self.lastMatchKeycodeList = []
			print ("function map ----- NO MATCH FOUND ++++++++++++")
			return False

		lastMatchString = self.bestMatchInputString
		self.bestMatchInputString = bestMatchStr
		#print ("function map ----- currentWord is ", currentWord)
		dbg5print ("################function map ----- bestMatchStr is ", bestMatchStr)

		matchType = self.wState.varna[bestMatchStr]

		#dbg4print ("=======S====== self.processState is now ", self.processState, ". Seeing=======: ", bestMatchStr, " matchType - ", matchType)
		#if "STANDALONE" in matchType: #JOINSTANDALONE, DEADSTANDALONE or STANDALONE
		#	dbg4print ("---------------->seeing STANDALONE, match is DeadStandalone = ", matchType == "DEADSTANDALONE")
		#	if matchType == "DEADSTANDALONE": #handle khanda ta!!
		#		if self.processState == "CONSONANT" or self.processState == "VIRAMA":
		#			#some consonant followed by khanda ta
		#			dbg3print ("---------------->seeing DEADSTANDALONE, self.processState == VIRAMA\n")
		#			keycodeList += self.wState.VIRAMA
		#			#some consonant followed by khanda ta
		#		keycodeList += self.wState.kc1[bestMatchStr]
		#	else:
		#		keycodeList += self.wState.kc1[bestMatchStr]
		#	self.processState = "START"
		#elif self.processState == "YAPHALA":
		#	if matchType == "CONSONANT":
		#		keycodeList += self.wState.ZWJ
		#		keycodeList += self.wState.VIRAMA
		#		dbg4print ("XXXXXXX ---+++---in state = ", self.processState, ", Seeing=======: bestMatchStr = ", bestMatchStr)
		#		#can come here only on context resume because keys 'd, r' entered will resume as d, VIRAMA, r
		#		#Or can be a special case for badly formatted UTF-8 texts where
		#		#a VIRAMA can be followed by space
		#		self.processState = "CONSONANT"
		#		keycodeList += self.wState.kc1[bestMatchStr]
		#elif self.processState == "VIRAMA":
		#	if matchType == "CONSONANT":
		#		dbg4print ("XXXXXXX ---+++---in state = ", self.processState, ", Seeing=======: bestMatchStr = ", bestMatchStr)
		#		#can come here only on context resume because keys 'd, r' entered will resume as d, VIRAMA, r
		#		#Or can be a special case for badly formatted UTF-8 texts where
		#		#a VIRAMA can be followed by space
		#		self.processState = "CONSONANT"
		#	elif matchType == "VOWEL":
		#		#special case for badly formatted UTF-8 texts where
		#		#a VIRAMA can be followed by space
		#		#here we always ensure VIRAMA is followed by ZWNJ so the state machine
		#		#can go back to S state
		#		dbg4print ("---+++---in state = ", self.processState, ", matchType = ", matchType)
		#		self.processState = "VOWEL"
		#	
		#	keycodeList += self.wState.VIRAMA
		#	keycodeList += self.wState.kc1[bestMatchStr]

		dbg5print ("--- at start  --- processstate = ", self.processState)
		if self.processState == "START":
			dbg5print ("++++in function map's START processstate -- matchType is ", matchType, " keycodeList = ", keycodeList)
			if matchType == "DEADCONSONANT":
				self.processState = "SD"
				keycodeList = self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "CONSONANT":
				self.processState = "CONSONANT"
				keycodeList = self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "VOWEL":
				#vowel at start of word
				self.processState = "STARTVOWEL"
				keycodeList = self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				#first add the full symbol for the first vowel in all Indic alphabets - 'a'
				if self.wState.firstVowel in self.wState.kc1.keys():
					keycodeList = self.wState.kc1[bestMatchStr]
				keycodeList += self.wState.kc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)

		elif self.processState == "CONSONANT":
			dbg5print ("--- at start of CONSONANT processstate")
			
			if matchType == "CONSONANTMODIFIER":
				#consonant modifier NUKTA
				self.processState = "CONSONANT"
				self.sendKeycodes(self.wState.kc1[bestMatchStr], ui)
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				#special treatment for antastha a
				#ra + ZWJ + VIRAMA + ya = rae
				#antastha a
				keycodeList = [self.wState.ZWJ]
				keycodeList += [self.wState.VIRAMA]
				keycodeList += self.wState.kc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif "CONSONANT" in matchType:
				dbg5print ("++++in function map's CONSONANT -- matchType is ", matchType, " keycodeList = ", keycodeList)
				#applies to all consonants
				#also applies to ra + VIRAMA + ya = rja
				#antastha ya
				if matchContinuation == True:
					dbg5print ("++++in function map's CONSONANT state, found CONS -- matchContinuation = ", matchContinuation)
					#h, last char was b, gives bh
					dbg5print ("++++in function map's CONSONANT state, found CONS -- self.lastMatchKeycodeList = ", self.lastMatchKeycodeList)
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = []
					if len(self.lastMatchKeycodeList) > 0:
						if self.lastMatchKeycodeList[0] == self.wState.VIRAMA:
							#a VIRAMA was deleted --> previous match db -> now dbh
							keycodeList = [self.wState.VIRAMA]
					self.processState = "CONSONANT"
				else:
					keycodeList = [self.wState.VIRAMA]
					self.processState = "CONSONANT"
					dbg5print ("++++in function map's CONSONANT -- added VIRAMA to keycodeList = ", keycodeList)
				keycodeList += self.wState.kc1[bestMatchStr]
				dbg5print ("++++in function map's CONSONANT -- added to keycodeList = ", keycodeList)
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWEL":
				if self.lastMatchType == "CONSONANT" and matchContinuation == True:
					#handle RI at start of word
					dbg5print ("++++in function map's CONSONANT state, found VOWEL -- matchContinuation = ", matchContinuation, " lastSTATE = START")
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					self.processState = "STARTVOWEL"
					keycodeList = self.wState.kc1[bestMatchStr]
				else:
					if matchContinuation == True:
						dbg5print ("++++in function map's CONSONANT state, found VOWEL -- matchContinuation = ", matchContinuation)
						self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					self.processState = "CONSONANTVOWEL"
					keycodeList = self.wState.kc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				self.sendKeycodes(self.wState.kc2[bestMatchStr], ui)
			dbg4print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg5print ("--- at end of CONSONANT state process, keycodeList list is ", keycodeList)
			self.lastMatchKeycodeList = keycodeList

		elif self.processState == "CONSONANTVOWEL":
			dbg5print ("--- at start of CONSONANTVOWEL state -- matchType is ", matchType)
			
			if matchType == "CONSONANTMODIFIER":
				#consonant modifier NUKTA
				self.processState = "CONSONANT"
				self.sendKeycodes(self.wState.kc1[bestMatchStr], ui)
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				#special treatment for antastha a
				#ra + ZWJ + VIRAMA + ya = rae
				#antastha a
				keycodeList = [self.wState.ZWJ]
				keycodeList += self.wState.VIRAMA
				keycodeList += self.wState.kc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif "CONSONANT" in matchType:
				dbg5print ("++++in function map's CONSONANTVOWEL state -- matchType is ", matchType)
				#applies to all consonants
				#also applies to ra + VIRAMA + ya = rja
				#antastha ya
				self.processState = "CONSONANT"
				keycodeList = self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "VOWEL":
				if matchContinuation == True:
					#a -> aa
					self.processState = "CONSONANTVOWEL"
					print ("VOWEL in CONSONANTVOWEL state with first vowel - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = self.wState.kc2[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "STARTVOWEL"
					keycodeList = self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				self.sendKeycodes(self.wState.kc1[bestMatchStr], ui)
			dbg4print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg4print ("--- at end of CONSONANT state process, glyph list is ", keycodeList)

		elif self.processState == "DEADCONSONANT":
			#DEADCONSONANT state is required only for handling proper 'bhartsanaa'
			dbg3print ("bhartsanaa - function map ----- self.processState is ", self.processState, "and matchType is ", matchType)
			if matchType == "DEADCONSONANT":
				self.processState = "CMANY"
				keycodeList = [self.wState.VIRAMA]
				keycodeList += self.wState.kc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif "CONSONANT" in matchType:
				self.processState = "CONSONANT"
				e2 = self.wState.kc2[bestMatchStr]
				if matchType == "LIVECONSONANT":
					#ta followed by antastha a or some other consonants that can combine with
					#ta without creating a khanda ta
					keycodeList = [self.wState.VIRAMA]
					if e2 == '_':
						#m, n, etc.
						keycodeList += self.wState.kc1[bestMatchStr]
					else:
						#ya-phala
						keycodeList += self.wState.kc2[bestMatchStr]
					self.sendKeycodes(keycodeList, ui)
				else:
					#ta followed by a consonant that is not an antastha a; can be antastha ya --> khanda ta + ya
					keycodeList = [self.wState.VIRAMA]
					keycodeList += [self.wState.ZWJ]
					keycodeList += [self.wState.ZWNJ]
					keycodeList += self.wState.kc1[bestMatchStr]
					self.sendKeycodes(keycodeList, ui)

			elif matchType == "CONSONANTMODIFIER":
				self.processState = "CONSONANT"
				keycodeList += self.wState.kc1[bestMatchStr]
			elif matchType == "VOWEL":
				self.processState = "STARTVOWEL"
				if self.wState.kc2[bestMatchStr] != "":
					keycodeList += self.wState.kc2[bestMatchStr]
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				keycodeList += self.wState.kc1[bestMatchStr]
			#dbg2print ("function map ----- self.processState is set to ", self.processState, "and matchType is ", matchType)

		elif self.processState == "STARTVOWEL":
			dbg5print ("++++in function map's VOWEL -- matchType is ", matchType)

			if matchType == "CONSONANTMODIFIER":
				#nukta after vowel is rare
				self.processState = "REPEATEDVOWEL"
				keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "DEADCONSONANT" or matchType == "CONSONANT":
				self.processState = "CONSONANT"
				keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "VOWEL":
				dbg5print ("++++in function map's STARTVOWEL state -- matchType is ", matchType)
				#dbg2print ("++++in function map's VOWEL -- len(bestMatchStr) is ", len(bestMatchStr))
				if matchContinuation == True and lastMatchString == self.wState.firstVowel:
					#a -> aa
					self.processState = "REPEATEDVOWEL"
					print ("aa found - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = self.wState.kc1[bestMatchStr]
				elif matchContinuation == True:
					self.processState = "STARTVOWEL"
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = self.wState.kc1[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "START"
					self.bestMatchInputString = ''
					keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				keycodeList = self.wState.kc1[bestMatchStr]

			self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

			dbg2print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg2print ("--- glyph list  is now ", keycodeList)
			
		elif self.processState == "REPEATEDVOWEL":
			dbg3print ("++++in function map's VOWEL -- matchType is ", matchType)

			if matchType == "CONSONANTMODIFIER":
				#nukta after vowel is rare
				self.processState = "REPEATEDVOWEL"
				keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "DEADCONSONANT" or matchType == "CONSONANT":
				self.processState = "CONSONANT"
				keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "VOWEL":
				dbg5print ("++++in function map's REPEATEDVOWEL state -- matchType is ", matchType)
				#dbg2print ("++++in function map's VOWEL -- len(bestMatchStr) is ", len(bestMatchStr))
				if matchContinuation == True and lastMatchString == self.wState.firstVowel:
					#a -> aa
					self.processState = "VOWEL"
					print ("aa found - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = self.wState.kc1[bestMatchStr]
				elif matchContinuation == True:
					self.processState = "VOWEL"
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = self.wState.kc2[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "START"
					self.bestMatchInputString = ''
					keycodeList = self.wState.kc1[bestMatchStr]
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.bestMatchInputString = ''
				self.lastMatchKeycodeList = []
				keycodeList = self.wState.kc1[bestMatchStr]

			self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

			dbg2print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg2print ("--- glyph list  is now ", keycodeList)

		else:
			self.processState = "START"
			self.bestMatchInputString = ''
			self.lastMatchKeycodeList = []
			dbg3print ("DEFAULT switch: self.processState is now set to S" )

		#dbg2print ("function map: now calling sendKeycodes -------")
		
		#print ("---function map calling sendKeycodes with glyph list ", keycodeList)
		#self.sendKeycodes (keycodeList, ui)
		dbg2print ("function map: returned from sendKeycodes, bestMatchStr and currentWord --->", bestMatchStr, " --------- ", currentWord)
		self.lastMatchType = matchType
		dbg2print ("====================== map done ====================================\n")
		return True

	#enddef

	#def loop (self, 

class TkApp(threading.Thread):
	def __init__(self, sibling=None):
		self.quitNow = False
		threading.Thread.__init__(self)
		self.sibling = sibling
		self.start()

	def consoleQuitCallback(self):
		print ("consoleQuitCallback: in TkApp")
		self.quitNow = True

	def run(self):
		self.root = tk.Tk()
		self.root.wm_attributes('-topmost', True)
		self.root.wm_attributes('-type', 'toolbar')
		self.root.resizable(False, False)
		self.root.update_idletasks()
		self.root.title("Keymap")
		self.root.protocol("WM_DELETE_WINDOW", self.consoleQuitCallback)
		self.tkAppKbd = tk.IntVar()
		self.tkAppKbd.set(1)
		frame = tk.Frame(self.root)
		label = tk.Label(self.root, text="Press Shift+Escape\nto quit Keymap.")
		buttonD = tk.Radiobutton(self.root, text="Devanagari", justify=tk.LEFT, variable=self.tkAppKbd, value=1, command=self.tkAppclick)
		buttonB = tk.Radiobutton(self.root, text="Bengali", justify=tk.LEFT, variable=self.tkAppKbd, value=2, command=self.tkAppclick)
		buttonL = tk.Radiobutton(self.root, text="Latin/US", justify=tk.LEFT, variable=self.tkAppKbd, value=3, command=self.tkAppclick)
		label.pack()
		frame.pack()
		buttonD.pack(anchor = tk.W)
		buttonB.pack(anchor = tk.W)
		buttonL.pack(anchor = tk.W)
		#buttonL.bind("<Button-1>", self.tkAppclick)
		while not self.quitNow:
			self.root.update()
			sleep(0.01)
		self.root.quit()

	def tkAppclick(self):
		if self.tkAppKbd.get() == 1:
			print ("enabled Dev KBD")
			self.sibling.skipMapping = False
			self.sibling.translitScheme = "dev"
			self.sibling.loadXKB("dev")
			self.sibling.wState.parseMapfile("d.map")
		elif self.tkAppKbd.get() == 2:
			print ("enabled Ben KBD")
			self.sibling.skipMapping = False
			self.sibling.translitScheme = "ben"
			self.sibling.loadXKB("ben")
			self.sibling.wState.parseMapfile("b.map")
		elif self.tkAppKbd.get() == 3:
			print ("enabled Latin/US KBD")
			self.sibling.skipMapping = True
			self.sibling.translitScheme = "none"
			self.sibling.loadXKB("us")

################ main ################
rmpr = remapper()
app = TkApp(rmpr)
rmpr.setConsoleQuitFunction(app.consoleQuitCallback)
rmpr.loop()
app.join()
try:
	rmpr.keyboard.ungrab()
	rmpr.keyboard.close()
	rmpr.ui.close()
except:
	print("EvDev/UInput already closed.")
subprocess.run(["/usr/bin/setxkbmap", "us"])
