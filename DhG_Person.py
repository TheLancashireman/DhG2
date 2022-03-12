#!/usr/bin/python3

# Person class - represent a person in the database

import os
import sys
from DhG_Event import Event

evchars = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?'])

class Person:
	def __init__(self):
		self.filename = None
		self.headlines = []
		self.events = []
		self.footlines = []
		self.name = None
		self.uniq = None
		self.sex = None
		self.father_name = None
		self.father_uniq = None
		self.mother_name = None
		self.mother_uniq = None

	# Read and store all the data from a person's card file
	#
	def ReadFile(self, filename):
		self.filename = filename
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

	# Normalise a name string: remove leading and trailing whitespace, replace multiple whitespace with a single space
	# Returns the normalised name
	#
	def NormaliseName(self, name):
		return ' '.join(name.split())

	# Extract the important information from the header lines:
	# Name, Uniq, Sex, Father, Mother
	#
	def AnalyseHeader(self):
		for line in self.headlines:
			line = line.lstrip()	# Remove leading spaces
			if line[0:5].lower() == 'name:':
				name = self.NormaliseName(line[5:])
				self.name = name
			elif line[0:5].lower() == 'uniq:':
				try:
					uniq = int(line[5:].rstrip().lstrip())
				except:
					uniq = None
				self.uniq = uniq
			elif line.lower() == 'male':
				self.sex = 'm'
			elif line.lower() == 'female':
				self.sex = 'f'
			elif line[0:7].lower() == 'mother:':
				(self.mother_name, self.mother_uniq) = self.ParseCombinedNameString(line[7:])
			elif line[0:7].lower() == 'father:':
				(self.father_name, self.father_uniq) = self.ParseCombinedNameString(line[7:])

	# Parse a combined name/id string in the form 'Forename Name Lastname [id]'
	# Returns normalised name and id as a tuple.
	#
	def ParseCombinedNameString(self, namestr):
		idx = namestr.find('[')
		if idx < 0:
			# Just a name
			name = namestr
			uniq = None
		else:
			name = namestr[0:idx]
			ustr = namestr[idx+1:]
			idx = ustr.find(']')
			if idx < 0:
				# Format error. Try to recover
				print('Error: no closing bracket after unique id')
			else:
				ustr = ustr[0:idx]
			ustr = ustr.rstrip().lstrip()
			try:
				uniq = int(ustr)
			except:
				# Format error: assume no unique ID
				name = namestr
				uniq = None
		return (self.NormaliseName(name), uniq)

	# Print all the info
	#
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
		print('File =', self.filename)
		print('Name =', self.name)
		print('Uniq =', self.uniq)
		print('Sex =', self.sex)
		print('Father =', self.father_name, '['+str(self.father_uniq)+']')
		print('Mother =', self.mother_name, '['+str(self.mother_uniq)+']')
