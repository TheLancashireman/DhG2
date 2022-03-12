#!/usr/bin/python3

# Person class - represent a person in the database

import os
import sys
from DhG_Event import Event

evchars = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?'])

class Person:
	def __init__(self):
		self.headlines = []
		self.events = []
		self.footlines = []
		self.name = None
		self.uniq = None
		self.father_name = None
		self.father_uniq = None
		self.mother_name = None
		self.mother_uniq = None

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

	def AnalyseHeader(self):
		for line in self.headlines:
			line = line.lstrip()	# Remove leading spaces
			if line[0:5].lower() == 'name:':
				name = ' '.join(line[5:].split())
				self.name = name
			elif line[0:5].lower() == 'uniq:':
				try:
					uniq = int(line[5:].rstrip().lstrip())
				except:
					uniq = None
				self.uniq = uniq

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

		print()
		print('======== Extracted data ========')
		print('Name =', self.name)
		print('Uniq =', self.uniq)
		print('Father =', self.father_name, '['+str(self.father_uniq)+']')
		print('Mother =', self.mother_name, '['+str(self.mother_uniq)+']')
