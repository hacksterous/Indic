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
from os import path, getcwd
from sys import exit as __exit
from sys import excepthook as __excepthook
from time import sleep
import subprocess
import tkinter as tk
import tkinter.simpledialog
import tkinter.messagebox
import threading
import pexpect
from select import select
import traceback

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

def handleGUIException(excType, excValue, excTraceback):
	errMsg = 'Fatal error seen, Indic will close.\nSend the error trace to <anirbax@gmail.com>.\n\n'
	errMsg.join(traceback.format_exception(excType, excValue, excTraceback))
	print (errMsg)
	tk.messagebox.showerror(title="Error", message=errMsg)
	__exit(1)

__excepthook = handleGUIException

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

		self.currentKeyboard = kbd
		self.charmap1 = {}
		self.charmap2 = {}
		self.firstVowel = {'dev': '', 'ben': ''}
		self.varna = {'dev': {}, 'ben': {}}
		self.kc1 = {'dev': {}, 'ben': {}}
		self.kc2 = {'dev': {}, 'ben': {}}
		self.currentVarna = {}
		self.currentKc1 = {}
		self.currentKc2 = {}
		self.currentFirstVowel = ''

		fileDone = self.parseKeycodefile("keycode.map")
		if kbd in ["dev", "ben"]:
			fileDone = self.parseMapfile(kbd)
			if fileDone:
				self.currentVarna = self.varna[kbd]
				self.currentKc1 = self.kc1[kbd]
				self.currentKc2 = self.kc2[kbd]
				self.currentFirstVowel = self.firstVowel[kbd]

	def parseKeycodefile (self, fileName=None):
		retVal = True
		#print ("parseKeycodefile: fileName is ...", fileName)
		#print ("parseKeycodefile: opening file fileName is ...", fileName)
		try:
			with open(fileName, "r") as f:
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
			print ("Error: Map file "+fileName+" was not found.", caption="Keycode File Error")
			retVal = False

		#for i in self.charmap1.keys():
			#print (i, " -> ", self.charmap1[i])
		return retVal

	def switchToMapfile (self, fName=None, dontErasePreviousMaps=False):
		#self.parseMapfile(fName, dontErasePreviousMaps)
		self.currentVarna = self.varna[kbd]
		self.currentKc1 = self.kc1[kbd]
		self.currentKc2 = self.kc2[kbd]
		self.currentFirstVowel = self.firstVowel[kbd]

	def parseMapfile (self, fName=None, dontErasePreviousMaps=False):
		#do not clear reverse and ucode dicts
		#as these might be needed for mixed texts
		if dontErasePreviousMaps == False:
			self.varna[fName].clear()
			self.kc1[fName].clear()
			self.kc2[fName].clear()
			self.firstVowel[fName] = ''

		retVal = True
		fileName = fName + ".map"
		#print ("parseMapfile: fileName is ...", fileName)
		#print ("parseMapfile: opening file fileName is ...", fileName)
		try:
			with open(fileName, "r") as f:
				for line in f:
					#print (line)
					key, v, kc1,kc2 = '_', '_', '_', '_'
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
					if len(lineList) == 4:
						key, v, kc1, kc2 = lineList 
						#print ("key is ---", key)
					else:
						print('Warning: Illegal Map File')
						print (lineList)
						retVal = False
						break
						
					self.kc1[fName][key] = []
					self.kc1[fName][key] += kc1.split('+')
					
					self.varna[fName][key] = v.upper()
					self.kc2[fName][key] = []
					self.kc2[fName][key] += kc2.split('+')

					if self.varna[fName][key] == "VOWEL" and self.kc2[fName][key] == ['_']:
						#first/default vowel is one that does not have the 2nd keycode/encoding
						self.firstVowel[fName] = key
						#print ("########~~~~~~~~ firstVowel = ", self.firstVowel[fName])

					#print ("key -- values ", key, self.varna[fName][key], self.kc1[fName][key], self.kc2[fName][key])
				#endfor
		except FileNotFoundError:
			print ("Error: Map file "+fileName+" was not found.")
			retVal = False

		self.VIRAMA = '32'
		self.ZWJ = 'SA41'
		self.ZWNJ = 'A41'
		self.REPHCONS = '36'

		#for i in self.kc1.keys():
		#	print (i, " -> ", self.kc1[i], end='')
		#	print (" -> ", self.kc2[i])
		return retVal

class remapper():
	def __init__(self, keyboardID = 'keyboard', mouseID = 'mouse', touchpadID = 'touchpad'):

		self.homePath = path.dirname(path.realpath(__file__))
		self.currentWorkDir = getcwd()
		self.userHomePath = path.expanduser("~")
		#print ("homepath = ", self.homePath)
		# Find all input devices.
		self.noMatchCount = 0
		self.waitForSendKeysComplete = False
		self.consoleQuitFunction = None
		self.ioLoopQuitNow = False
		self.skipMapping = False
		self.translitScheme = "dev"
		self.loadDevanagari = True
		self.lastMatchString = ''
		self.bestMatchInputString = ''
		self.lastMatchKeycodeList = []
		self.processState = "START"
		self.shiftStateEcode = 0
		self.shiftState = False #KEY_LEFTSHIFT or KEY_RIGHTSHIFT has been pressed
		self.ctrlAltState = False #left/right control or alt has been pressed
		devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		# Limit the list to those containing keyboardID and pick the first one.
		if len(devices) == 0:
			tk.messagebox.showerror(title="Error", message="Error: can't access device (/dev/event*).\nPlease check permissions.\n $ sudo usermod -a -G input <your_username>")
			print("Error: can't access device (/dev/event*)")
			__exit(1)
			
		kList = [d for d in devices if keyboardID in d.name.lower()]
		mList = [d for d in devices if mouseID in d.name.lower()]
		tList = [d for d in devices if touchpadID in d.name.lower()]

		if len(kList) > 0:
			self.keyboard = kList[0]
		else:
			tk.messagebox.showerror(title="Error", message="Error: No keyboard was found - can't proceed.")
			print("Error: No keyboard was found - can't proceed.")
			__exit(1)

		self.mouse = self.touchpad = None
		if len(mList) > 0:
			self.mouse = mList[0]
		if len(tList) > 0:
			self.touchpad = tList[0]

		self.deviceDict = {self.keyboard.fd: self.keyboard, 
							self.mouse.fd: self.mouse, 
							self.touchpad.fd: self.touchpad}
		#self.inputdevices = {self.keyboard, self.mouse, self.touchpad}
		print ("mouse - ", self.mouse)
		print ("touchpad - ", self.touchpad)
		print ("keyboard - ", self.keyboard)

		getPassword = False
		try:
			self.ui = evdev.UInput.from_device(self.keyboard)
		except:
			getPassword = True

		if getPassword == True:
			sudoCount = 3
			command = 'sudo chmod +0666 /dev/uinput'
			message = ""
			while sudoCount > 0:
				message += "Enter admin password to enable writing into \nthe UInput device (/dev/uinput):"

				passwd = tk.simpledialog.askstring("Password", message, show='*')
				if passwd == None:
					print ("Received None from dialog")
					sudoCount = 100
					break
				else:
					passwd += '\n'
				(output, retval) = pexpect.run (command, events={'\[sudo\] password for .*\: ': passwd}, timeout=1, withexitstatus=1)
				print ("pexpect.run returned ", retval)

				if retval != 0:
					print ("Password did not work")
					sudoCount -= 1
					message = str(sudoCount) + " attempts left. Try again. "
				else:
					sudoCount = -1
					break
			
			if sudoCount == 100: 
				tk.messagebox.Message(title="Error", message="Error: No valid password received.")
				print ("Bailed out.")
				__exit(1)
			elif sudoCount == 0: #three unsuccessful attempts
				tk.messagebox.Message(title="Error", message="Error: can't open the UInput device (/dev/uinput)")
				print("Error: can't open the UInput device (/dev/uinput)")
				__exit(1)
			elif sudoCount == -1:
				#/dev/uinput is writable now 
				print ("Got password correctly.")
				self.ui = evdev.UInput.from_device(self.keyboard)

		try:
			self.keyboard.grab()  # Grab, i.e. prevent the keyboard from emitting original events.
		except:
			tk.messagebox.showerror(title="Error", message="Error: can't open the Evdev \nkeyboard device (/dev/uinput)")
			print("Error: can't open the Evdev device (/dev/input/*)")
			__exit(1)

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
		#flush out existing chars in keyboard buffer
		while self.keyboard.read_one() != None:
			pass
		while not self.ioLoopQuitNow:
			r, w, x = select(self.deviceDict, [], [])
			for fd in r:
				if fd == None:
					continue
				for event in self.deviceDict[fd].read():
					if self.waitForSendKeysComplete == True:
						continue
					if event.type == evdev.ecodes.EV_KEY:  # Process key and mouse events.
						#print ("event code = ", event.code, " = ")
						#print (evdev.ecodes.KEY[event.code], " event value = ", event.value)
						if event.code == evdev.ecodes.KEY_ESC and event.value == 1 and event.type == 1: #check for the event.type, 1 is KEY
							# Exit on pressing Shift+ESC.
							#print ("loop: seeing ESCAPE self.shiftState is ", self.shiftState)
							if self.shiftState == True:
								self.consoleQuitFunction()
								self.ioLoopQuitNow = True
								break
							else:
								if event.value == 1:
									print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~RESETTING to START A.")
									self.noMatchCount = 0
									self.bestMatchInputString = ''
									self.processState = "START"
									self.lastMatchKeycodeList = []
								ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
								ui.syn()
								sleep(0.002)
						elif event.code in [evdev.ecodes.KEY_LEFTCTRL, evdev.ecodes.KEY_RIGHTCTRL,
												evdev.ecodes.KEY_LEFTALT, evdev.ecodes.KEY_RIGHTALT]:
							self.ctrlAltState = False
							if event.value == 1:
								self.ctrlAltState = True
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
							ui.syn()
							sleep(0.002)
						elif event.code not in NOREMAP_KEYLIST and event.value == 1 and self.skipMapping == False and event.type == 1:
							#print ("ELIF not in NOREMAP_KEYLIST: event code = ", event.code, " = ", evdev.ecodes.KEY[event.code], " event value = ", event.value)
							#touchpad gestures register here -- we don't want these
							if fd == self.mouse.fd or fd == self.touchpad.fd:
								continue
							if event.code in self.wState.charmap1.keys():
								if self.ctrlAltState == True:
									print ("#####===== got a keycode ", event.code, " when self.ctrlAltState = ", self.ctrlAltState)
									print ("#####===== this is ASCII ", self.wState.charmap1[event.code], " when self.ctrlAltState = ", self.ctrlAltState)
									#ui.write(evdev.ecodes.EV_KEY, , event.value) 
									#FIXME //map ascii codes to new keycodes using xmodmap so that ctrl+ascii can be passed on
									#ui.syn()
									#sleep(0.002)
									#continue
									pass
									
								if self.shiftState == True:
									#print("keycode charmap1 = ", self.wState.charmap2[event.code])
									currentInputChar = self.wState.charmap2[event.code]
								else:
									#print("keycode charmap1 = ", self.wState.charmap1[event.code])
									currentInputChar = self.wState.charmap1[event.code]
							handled = self.map(currentInputChar, ui)
							if handled == False:
								#pass on unhandled events
								if self.noMatchCount > 5:
									print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~RESETTING to START B.")
									self.processState = "START"
									self.noMatchCount = 0
									self.bestMatchInputString = ''
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
							self.bestMatchInputString = ''
							self.noMatchCount = 0
							self.processState = "START"
							self.lastMatchKeycodeList = []
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
							ui.syn()
							sleep(0.002)
							#print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PASSTHRU Y.")
							while self.deviceDict[fd].read_one() != None:
								pass
							sleep(0.1) #sleep 100ms more
						else:
							# Passthrough other key events unmodified.
							#print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PASSTHRU X"
							ui.write(evdev.ecodes.EV_KEY, event.code, event.value) 
							ui.syn()
							sleep(0.002)
					else:
						#print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PASSTHRU Y.")
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
		subprocess.run(["/usr/bin/setxkbmap", "-layout", kbd])
		if kbd in ["ben", "dev"]:
			cmdarg = self.homePath + "/Indic-" + kbd + ".xmodmap"
			#print ("homepath = ", self.homePath, ", cmdarg = ", cmdarg)

			#for default Bengali keyboard, add the ZWNJ and ZWJ characters
			#add OM character and khaNDa ta
			#v is b with a diagonal at bottom = Bengali va and avagraha
			#1 and exclam sign
			#4 and rupee sign
			#map shift+space to single quote
			#shift+backspace is double quote
			subprocess.run(["/usr/bin/xmodmap", cmdarg])

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
		if keycodeList in [[], ["_"]]:
			return
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
		dbg5print ("function map ----- currentWord is ", currentWord)
		#dbg5print ("function map ----- shiftState is ", currentWord)
		dbg4print ("function map ----- len currentWord is ", len(currentWord))
		#print(currentWord[0:endIndex] in self.wState.currentKc1.keys())
		if currentWord in self.wState.currentKc1.keys():
			matchFound = 1
			bestMatchStr = currentWord
			if self.bestMatchInputString in self.wState.currentKc1.keys():
				matchContinuation = True
		elif currentChar in self.wState.currentKc1.keys():
			matchFound = 1
			bestMatchStr = currentChar

		self.lastMatchType = self.processState
		if matchFound == 0:
			if self.noMatchCount == 0:
				self.bestMatchInputString = ''
			self.noMatchCount += 1
			self.bestMatchInputString += currentChar
			if self.noMatchCount > 5:
				#give up after 5 unsuccessful attempts at match
				self.noMatchCount = 0
				self.bestMatchInputString = ''
				self.processState = "START"
				self.lastMatchKeycodeList = []
				print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~RESETTING to START D.")
			print ("function map ----- NO MATCH FOUND ++++++++++++, self.bestMatchInputString = ", self.bestMatchInputString)
			return False

		lastBeforeMatchString = self.lastMatchString
		self.lastMatchString = self.bestMatchInputString
		self.bestMatchInputString = bestMatchStr
		#print ("function map ----- currentWord is ", currentWord)
		dbg5print ("################function map ----- bestMatchStr is ", bestMatchStr)

		matchType = self.wState.currentVarna[bestMatchStr]

		dbg5print ("--- at start  --- processstate = ", self.processState)
		if self.processState == "START":
			dbg5print ("++++in function map's START processstate -- matchType is ", matchType, " keycodeList = ", keycodeList)
			if matchType in ["CONSONANT", "LIVECONSONANT", "DEADCONSONANT"] :
				if matchType == "DEADCONSONANT":
					self.processState = "DEADCONSONANT"
				else:
					self.processState = "STARTCONSONANT"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWEL":
				#vowel at start of word
				self.processState = "STARTVOWEL"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				dbg5print ("--- set processstate to STARTVOWEL")
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				#first add the full symbol for the first vowel in all Indic alphabets - 'a'
				keycodeList = []
				if self.wState.currentFirstVowel in self.wState.currentKc1.keys():
					keycodeList += self.wState.currentKc1[self.wState.currentFirstVowel]
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "STANDALONE":
				self.processState = "START"
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

		elif self.processState == "STARTCONSONANT":
			#only to handle RI/LI
			dbg5print ("--- at start of STARTCONSONANT processstate")
			dbg5print ("--- at start of CONSONANT processstate, received matchType = ", matchType)
			if matchType == "CONSONANTMODIFIER":
				#consonant modifier NUKTA
				self.processState = "CONSONANT"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				#special treatment for antastha a
				#ra + ZWJ + VIRAMA + ya = rae
				#antastha a
				#keycodeList = self.wState.ZWJ
				keycodeList = []
				keycodeList.append(self.wState.VIRAMA)
				keycodeList += self.wState.currentKc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType in ["CONSONANT", "LIVECONSONANT"]:
				dbg5print ("++++in function map's STARTCONSONANT state -- matchType is ", matchType, " keycodeList = ", keycodeList)
				#applies to all consonants
				#also applies to ra + VIRAMA + ya = rja
				#antastha ya
				if matchContinuation == True:
					dbg5print ("++++in function map's STARTCONSONANT state, found CONS -- matchContinuation = ", matchContinuation)
					#h, last char was b, gives bh
					dbg5print ("++++in function map's STARTCONSONANT state, found CONS -- self.lastMatchKeycodeList = ", self.lastMatchKeycodeList)
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = []
					if len(self.lastMatchKeycodeList) > 0:
						if self.lastMatchKeycodeList[0] == self.wState.VIRAMA:
							#a VIRAMA was deleted --> previous match db -> now dbh
							keycodeList = self.wState.VIRAMA
					self.processState = "CONSONANT"
					keycodeList += self.wState.currentKc1[bestMatchStr]
				elif matchType == "CONSONANT" and self.wState.currentKc2[bestMatchStr] != ["_"]:
					#should match 'Y' (uppercase)
					keycodeList = []
					if self.wState.currentKc2[bestMatchStr] != ['_']:
						keycodeList.append(self.wState.ZWNJ)
						keycodeList.append(self.wState.VIRAMA)
						keycodeList += self.wState.currentKc2[bestMatchStr]
					dbg5print ("~~~~~~~~~~~~~~~~~~~self.wState.currentKc2[bestMatchStr] = ", self.wState.currentKc2[bestMatchStr], " for bestMatchStr = ", bestMatchStr, " keycodeList = ", keycodeList)
				else:
					keycodeList.append(self.wState.VIRAMA)
					self.processState = "CONSONANT"
					dbg5print ("++++in function map's STARTCONSONANT state -- added VIRAMA to keycodeList = ", keycodeList)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				dbg5print ("++++in function map's STARTCONSONANT state -- added to keycodeList = ", keycodeList)
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWEL":
				if matchContinuation == True:
					#handle RI at start of word
					dbg5print ("++++in function map's STARTCONSONANT state, found VOWEL -- matchContinuation = ", matchContinuation, " lastSTATE = START")
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					self.processState = "STARTVOWEL"
					keycodeList = []
					keycodeList += self.wState.currentKc1[bestMatchStr]
				else:
					self.processState = "CONSONANTVOWEL"
					keycodeList = []
					if self.wState.currentKc2[bestMatchStr] != ["_"]:
						keycodeList += self.wState.currentKc2[bestMatchStr]
				dbg5print ("++++in function map's STARTCONSONANT state, to call sendKeycodes -- keycodeList = ", keycodeList)
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.sendKeycodes(self.wState.currentKc1[bestMatchStr], ui)
			elif matchType == "STANDALONE":
				self.processState = "START"
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				#first add the full symbol for the first vowel in all Indic alphabets - 'a'
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)

			dbg4print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg5print ("--- at end of CONSONANT state process, keycodeList list is ", keycodeList)
			self.lastMatchKeycodeList = keycodeList

		elif self.processState == "CONSONANT":
			dbg5print ("--- at start of CONSONANT processstate, received matchType = ", matchType)
			
			if matchType == "CONSONANTMODIFIER":
				#consonant modifier NUKTA
				dbg5print ("--- at start of CONSONANT processstate, received CONSONANTMODIFIER")
				self.processState = "CONSONANT"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				#special treatment for antastha a
				#ra + ZWJ + VIRAMA + ya = rae
				#antastha a
				#keycodeList = self.wState.ZWJ
				keycodeList = []
				keycodeList.append(self.wState.VIRAMA)
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType in ["CONSONANT", "LIVECONSONANT"]:
				dbg5print ("++++in function map's CONSONANT -- matchType is ", matchType, " keycodeList = ", keycodeList)
				#applies to all consonants
				#also applies to ra + VIRAMA + ya = rja
				#antastha ya
				if matchContinuation == True:
					dbg5print ("++++in function map's CONSONANT state, found CONS -- matchContinuation = ", matchContinuation)
					#h, last char was b, gives bh
					dbg5print ("++++in function map's CONSONANT state, found matchType = ", matchType, " -- self.lastMatchKeycodeList = ", self.lastMatchKeycodeList)
					dbg5print ("++++in function map's CONSONANT state, lastBeforeMatchString = ", lastBeforeMatchString, " -- self.lastMatchString = ", self.lastMatchString)
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = []
					if len(self.lastMatchKeycodeList) > 0:
						if self.lastMatchKeycodeList[0] == self.wState.VIRAMA:
							#a VIRAMA was deleted --> previous match db -> now dbh
							keycodeList.append(self.wState.VIRAMA)
					self.processState = "CONSONANT"
					keycodeList += self.wState.currentKc1[bestMatchStr]
				elif matchType == "CONSONANT" and self.wState.currentKc2[bestMatchStr] != ["_"]:
					#should match 'Y' (uppercase)
					keycodeList = []
					if self.wState.currentKc2[bestMatchStr] != ['_']:
						keycodeList.append(self.wState.ZWNJ)
						keycodeList.append(self.wState.VIRAMA)
						keycodeList += self.wState.currentKc2[bestMatchStr]
					dbg5print ("~~~~~~~~~~~~~~~~~~~self.wState.currentKc2[bestMatchStr] = ", self.wState.currentKc2[bestMatchStr], " for bestMatchStr = ", bestMatchStr, " keycodeList = ", keycodeList)
				else:
					keycodeList = []
					keycodeList.append(self.wState.VIRAMA)
					self.processState = "CONSONANT"
					dbg5print ("++++in function map's CONSONANT -- added VIRAMA to keycodeList = ", keycodeList)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				dbg5print ("++++in function map's CONSONANT -- added to keycodeList = ", keycodeList)
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWEL":
				keycodeList = []
				if matchContinuation == True:
					dbg5print ("~~~++++in function map's CONSONANT state, found VOWEL -- matchContinuation = ", matchContinuation)
					dbg5print ("~~~++++in function map's CONSONANT state, found VOWEL -- self.lastMatchString = ", self.lastMatchString)
					dbg5print ("~~~++++in function map's CONSONANT state, found VOWEL -- lastBeforeMatchString = ", lastBeforeMatchString)
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					if self.wState.currentVarna[lastBeforeMatchString] == "DEADCONSONANT":
						#we got a khanDa ta + CONSONANT and CONSONANT matchContinues into a VOWEL - tRI
						#delete the khanDA ta
						self.deletePrevious(1, ui)
						keycodeList += self.wState.currentKc1[lastBeforeMatchString]
				self.processState = "CONSONANTVOWEL"
				if self.wState.currentKc2[bestMatchStr] != ['_']:
					keycodeList += self.wState.currentKc2[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				self.sendKeycodes(self.wState.currentKc1[bestMatchStr], ui)
			elif matchType == "STANDALONE":
				self.processState = "START"
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				#first add the full symbol for the first vowel in all Indic alphabets - 'a'
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)

			dbg4print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg5print ("--- at end of CONSONANT state process, keycodeList list is ", keycodeList)
			self.lastMatchKeycodeList = keycodeList

		elif self.processState == "CONSONANTVOWEL":
			dbg5print ("--- at start of CONSONANTVOWEL state -- matchType is ", matchType)
			
			if matchType == "CONSONANTMODIFIER":
				#consonant modifier NUKTA
				self.processState = "CONSONANT"
				self.sendKeycodes(self.wState.currentKc1[bestMatchStr], ui)
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				#special treatment for antastha a
				#ra + ZWJ + VIRAMA + ya = rae
				#antastha a
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif "CONSONANT" in matchType:
				dbg5print ("++++in function map's CONSONANTVOWEL state -- matchType is ", matchType)
				#applies to all consonants
				#also applies to ra + VIRAMA + ya = rja
				#antastha ya
				self.processState = "CONSONANT"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType == "VOWEL":
				if matchContinuation == True:
					#a -> aa
					self.processState = "CONSONANTVOWEL"
					dbg4print ("VOWEL in CONSONANTVOWEL state with first vowel - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList = []
					if self.wState.currentKc2[bestMatchStr] != ['_']:
						keycodeList += self.wState.currentKc2[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "STARTVOWEL"
					keycodeList = []
					keycodeList += self.wState.currentKc1[bestMatchStr]
				self.sendKeycodes(keycodeList, ui)
				self.lastMatchKeycodeList = keycodeList
			elif matchType in ["VOWELMODIFIER", "STANDALONE"]:
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				self.processState = "START"
				self.sendKeycodes(self.wState.currentKc1[bestMatchStr], ui)
			dbg4print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg4print ("--- at end of CONSONANT state process, glyph list is ", keycodeList)

		elif self.processState == "DEADCONSONANT":
			dbg5print ("- function map ----- self.processState is ", self.processState, " and matchType is ", matchType, " matchContinuation = ", matchContinuation)
			dbg5print ("- function map ----- bestMatchStr is ", bestMatchStr, " matchContinuation = ", matchContinuation)
			if matchType in ["DEADCONSONANT", "LIVECONSONANT"]:
				#tt, or tn, tb, tm, ty, tr, tl, tv
				self.processState = "CONSONANT"
				keycodeList = []
				keycodeList.append(self.wState.VIRAMA)
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType in ["VOWELMODIFIER", "STANDALONE"]:
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				self.processState = "START"
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "CONSONANT":
				#regular consonant after t (DEADCONSONANT) creates a khaNDa ta
				#t + k + c varga, tp, tph, tbh, ts, tsh, tS, th
				dbg5print ("################function map --- regular consonant after t (DEADCONSONANT) --- matchType is ", matchType, " self.lastMatchString = ", self.lastMatchString)
				dbg5print ("################function map --- regular consonant after t (DEADCONSONANT) --- lastBeforeMatchString = ", lastBeforeMatchString)
				dbg5print ("################function map --- regular consonant after t (DEADCONSONANT) --- self.lastMatchKeycodeList[0] = ", self.lastMatchKeycodeList[0])
				if lastBeforeMatchString in self.wState.currentKc1.keys():
					dbg5print ("################function map --- regular consonant after t (DEADCONSONANT) --- self.wState.currentKc1[lastBeforeMatchString] = ", self.wState.currentKc1[lastBeforeMatchString])

				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				else:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					if self.lastMatchKeycodeList[0] == self.wState.VIRAMA and self.wState.currentKc1[lastBeforeMatchString] == [self.wState.REPHCONS]:
						#special case only for rt+regular cons
						keycodeList = [self.wState.VIRAMA]
					else:
						keycodeList = []
					if self.wState.currentKc2[self.lastMatchString] != ['_']:
						keycodeList += self.wState.currentKc2[self.lastMatchString] 
					self.sendKeycodes(keycodeList, ui)
				self.processState = "CONSONANT"
				#ta followed by a consonant that is not an antastha a; can be antastha ya --> khanda ta + ya
				keycodeList = []
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "CONSONANTMODIFIER":
				self.processState = "CONSONANT"
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "VOWEL":
				self.processState = "STARTVOWEL"
				if self.wState.currentKc2[bestMatchStr] != ["_"]:
					keycodeList += self.wState.currentKc2[bestMatchStr]
			elif matchType in ["VOWELMODIFIER", "STANDALONE"]:
				self.processState = "START"
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				keycodeList += self.wState.currentKc1[bestMatchStr]
			#dbg2print ("function map ----- self.processState is set to ", self.processState, "and matchType is ", matchType)

			self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

		elif self.processState == "STARTVOWEL":
			dbg5print ("++++in function map processState is STARTVOWEL -- matchType is ", matchType)
			keycodeList = []
			if matchType == "CONSONANTMODIFIER":
				#nukta after vowel is rare
				self.processState = "REPEATEDVOWEL"
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "DEADCONSONANT":
				self.processState = "DEADCONSONANT"
				keycodeList += self.wState.currentKc1[bestMatchStr]
				dbg5print ("++++set processState to DEADCONSONANT -- matchType is ", matchType)
			elif matchType in ["CONSONANT", "LIVECONSONANT"]:
				self.processState = "CONSONANT"
				if matchType == "CONSONANT" and self.wState.currentKc2[bestMatchStr] != ["_"]:
					dbg5print ("~~~~~~~~~~~~~~~~~~~ in state VOWEL, bestMatchStr = *CONSONANT self.wState.currentKc2[bestMatchStr] = ", self.wState.currentKc2[bestMatchStr], " for bestMatchStr = ", bestMatchStr, " keycodeList = ", keycodeList)
					if self.wState.currentKc2[bestMatchStr] != ['_']:
						keycodeList.append(self.wState.ZWNJ)
						keycodeList.append(self.wState.VIRAMA)
						keycodeList += self.wState.currentKc2[bestMatchStr]
				else:
					keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "VOWEL":
				dbg5print ("++++in function map's STARTVOWEL state -- matchType is ", matchType, " matchContinuation = ",  matchContinuation)
				#dbg2print ("++++in function map's VOWEL -- len(bestMatchStr) is ", len(bestMatchStr))
				keycodeList = []
				if matchContinuation == True and self.lastMatchString == self.wState.currentFirstVowel:
					#a -> aa
					self.processState = "STARTVOWEL"
					print ("aa found - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				elif matchContinuation == True:
					self.processState = "STARTVOWEL"
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "START"
					keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType in ["VOWELMODIFIER", "STANDALONE"]:
				if matchContinuation == True and matchType == "STANDALONE":
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				self.processState = "START"
				keycodeList += self.wState.currentKc1[bestMatchStr]

			self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

			dbg2print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg2print ("--- glyph list  is now ", keycodeList)
			
		elif self.processState == "REPEATEDVOWEL":
			dbg3print ("++++in function map's VOWEL -- matchType is ", matchType)

			if matchType == "CONSONANTMODIFIER":
				#nukta after vowel is rare
				self.processState = "REPEATEDVOWEL"
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "DEADCONSONANT" or matchType == "CONSONANT":
				self.processState = "CONSONANT"
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "VOWEL":
				dbg5print ("++++in function map's REPEATEDVOWEL state -- matchType is ", matchType)
				#dbg2print ("++++in function map's VOWEL -- len(bestMatchStr) is ", len(bestMatchStr))
				if matchContinuation == True and self.lastMatchString == self.wState.currentFirstVowel:
					#a -> aa
					self.processState = "VOWEL"
					print ("aa found - len self.lastMatchKeycodeList = ", len(self.lastMatchKeycodeList))
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				elif matchContinuation == True:
					self.processState = "VOWEL"
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
					keycodeList += self.wState.currentKc1[bestMatchStr]
				else:
					#it's a vowel with just one phonetic (transliteration) 
					#character -- we must now show a full form vowel
					self.processState = "START"
					keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "VOWELMODIFIER":
				self.processState = "START"
				keycodeList += self.wState.currentKc1[bestMatchStr]
			elif matchType == "STANDALONE":
				if matchContinuation == True:
					self.deletePrevious(len(self.lastMatchKeycodeList), ui)
				self.processState = "START"
				self.sendKeycodes(self.wState.currentKc1[bestMatchStr], ui)

			self.sendKeycodes(keycodeList, ui)
			self.lastMatchKeycodeList = keycodeList

			dbg2print ("function map ----- self.processState is set to ", self.processState, " and matchType is ", matchType)
			dbg2print ("--- glyph list  is now ", keycodeList)

		else:
			self.processState = "START"
			self.bestMatchInputString = ''
			self.noMatchCount = 0
			self.lastMatchKeycodeList = []
			dbg5print ("~~~~~~~~~~~~~~~~~~~DEFAULT switch: self.processState is now set to START" )

		#dbg2print ("function map: now calling sendKeycodes -------")
		
		#print ("---function map calling sendKeycodes with glyph list ", keycodeList)
		#self.sendKeycodes (keycodeList, ui)
		dbg2print ("function map: returned from sendKeycodes, bestMatchStr and currentWord --->", bestMatchStr, " --------- ", currentWord)
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
		self.root.title("Indic")
		self.root.protocol("WM_DELETE_WINDOW", self.consoleQuitCallback)
		self.tkAppKbd = tk.IntVar()
		self.tkAppKbd.set(1)
		frame = tk.Frame(self.root)
		label = tk.Label(self.root, text="Press Shift+Escape\nto quit Indic.")
		buttonD = tk.Radiobutton(self.root, text="Devanagari", justify=tk.LEFT, variable=self.tkAppKbd, value=1, command=self.tkAppclick)
		buttonB = tk.Radiobutton(self.root, text="Bengali", justify=tk.LEFT, variable=self.tkAppKbd, value=2, command=self.tkAppclick)
		buttonL = tk.Radiobutton(self.root, text="Latin/US", justify=tk.LEFT, variable=self.tkAppKbd, value=3, command=self.tkAppclick)
		buttonQ = tk.Button(self.root, text="Quit")
		label.pack()
		frame.pack()
		buttonD.pack(anchor = tk.W)
		buttonB.pack(anchor = tk.W)
		buttonL.pack(anchor = tk.W)
		#buttonQ.pack(anchor = tk.S)
		#buttonQ.bind("<Button-1>", self.tkAppButtonQ)
		while not self.quitNow:
			self.root.update()
			sleep(0.01)
		self.root.quit()

	def tkAppButtonQ(self, event):
		self.quitNow = True
		print ("~~~~~~~~~~~~ set self.quitNow = ", self.quitNow)

	def tkAppclick(self):
		if self.tkAppKbd.get() == 1:
			print ("enabled Dev KBD")
			self.sibling.skipMapping = False
			self.sibling.translitScheme = "dev"
			self.sibling.loadXKB("dev")
			self.sibling.wState.switchToMapfile("dev")
		elif self.tkAppKbd.get() == 2:
			print ("enabled Ben KBD")
			self.sibling.skipMapping = False
			self.sibling.translitScheme = "ben"
			self.sibling.loadXKB("ben")
			self.sibling.wState.switchToMapfile("ben")
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
