#!/usr/bin/python3

# Person class - represent a person in the database

import os
import sys
from Event import Event

evchars = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?'])

class Person:
	def __init__(self):
		self.headlines = []
		self.events = []
		self.footlines = []

	def ReadFile(self, filename):
		mode = 0	# 0 = head, 1 = timeline, 2 = tail
		cur_event = None
		f = open(filename, 'r')
		for line in f:
			line = line.rstrip()	# Removes LF as well

			if line.lower() == 'eof':					# Go straight to footer
				if cur_event != None:				# Finish processing current event
					self.events.append(cur_event)
				cur_event = None
				mode = 2

			if mode == 0:
				if line[0:1] in evchars:
					mode = 1
				else:
					self.headlines.append(line)

			if mode == 1:
				if line[0:1] in evchars:
					if cur_event != None:
						self.events.append(cur_event)
					cur_event = Event()
				cur_event.AddLine(line)

			if mode == 2:
				self.footlines.append(line)

		f.close()

	def Print(self):	# For debugging
		print('======== Header ========')
		for ll in self.headlines:
			print(ll)

		for e in self.events:
			print('======== Event ========')
			for ll in e.lines:
				print(ll)

		print('======== Footer ========')
		for ll in self.footlines:
			print(ll)
