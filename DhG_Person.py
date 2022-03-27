#!/usr/bin/python3
#
# (c) David Haworth
#
# This file is part of DhG.
#
# DhG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DhG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DhG.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from DhG_Event import Event

evchars = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?'])


# Person class - represent a person in the database
#
class Person:
	def __init__(self):
		self.filename = None
		self.headlines = []
		self.events = []
		self.footlines = []
		self.name = None
		self.uniq = None
		self.sex = None
		self.birth = None
		self.death = None
		self.partnerships = []
		self.father_name = None
		self.father_uniq = None
		self.mother_name = None
		self.mother_uniq = None

	# Read and store all the data from a person's card file
	#
	def ReadFile(self, filename):
		self.filename = filename
		self.Read()

	def Read(self):
		# Clear out any old stuff
		self.headlines = []
		self.events = []
		self.footlines = []
		self.name = None
		self.uniq = None
		self.sex = None
		self.birth = None
		self.death = None
		self.partnerships = []
		self.father_name = None
		self.father_uniq = None
		self.mother_name = None
		self.mother_uniq = None
		mode = 0	# 0 = head, 1 = timeline, 2 = tail
		cur_event = None
		f = open(self.filename, 'r')
		for line in f:
			line = line.rstrip()	# Removes LF as well

			if line.lower() == 'eof':				# Go straight to footer
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

		if cur_event != None:
			self.events.append(cur_event)

		f.close()

	# Normalise a name string: remove leading and trailing whitespace, replace multiple whitespace with a single space
	# Returns the normalised name
	#
	@staticmethod
	def NormaliseName(name):
		return ' '.join(name.split())

	# Parse a combined name/id string in the form 'Forename Name Lastname [id]'
	# Returns normalised name and id as a tuple.
	#
	@staticmethod
	def ParseCombinedNameString(namestr):
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
				if ustr[idx+1:] != '':
					name = name + ' ' + ustr[idx+1:]
				ustr = ustr[0:idx]
			ustr = ustr.rstrip().lstrip()
			try:
				uniq = int(ustr)
			except:
				# Format error: assume no unique ID
				name = namestr
				uniq = None
		return (Person.NormaliseName(name), uniq)

	# Extract the important information from the header lines:
	# Name, Uniq, Sex, Father, Mother
	#
	def AnalyseHeader(self):
		for line in self.headlines:
			line = line.lstrip()	# Remove leading spaces
			if line[0:5].lower() == 'name:':
				name = Person.NormaliseName(line[5:])
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
				(self.mother_name, self.mother_uniq) = Person.ParseCombinedNameString(line[7:])
			elif line[0:7].lower() == 'father:':
				(self.father_name, self.father_uniq) = Person.ParseCombinedNameString(line[7:])

	# Return True if person matches arguments
	# arg is a list of terms. Result is true iff all terms match
	#
	def IsMatch(self, arg):
		if self.name != None:
			terms = arg.split()
			for t in terms:
				if self.name.lower().find(t.lower()) < 0:
					return False
			return True
		return False

	# Return a string containing vital information about the person
	# fmt specifies what to return			ToDo
	# datefmt spefies how to show dates		ToDo
	#
	def GetVitalLine(self, fmt, datefmt):
		idx_id = 0		# ToDo work out indexes from fmt parameter
		idx_name = 1
		idx_dates = 2
		parts = ['', '', '']
		if self.uniq == None:
			parts[idx_id] = '[?]'
		else:
			parts[idx_id] = '['+str(self.uniq)+']'
		if self.name == None:
			parts[idx_name] = '?'
		else:
			parts[idx_name] = self.name
		if self.birth == None:
			dob = '?'
		else:
			dob = self.birth.GetDate(0)
		if self.death == None:
			dod = ''
		else:
			dod = self.death.GetDate(0)
		parts[idx_dates] = '('+dob+'-'+dod+')'
		return ' '.join(parts)

	# Analyse all the events for this person
	#
	def AnalyseEvents(self):
		for e in self.events:
			e.DecodeEventType(self)
			if e.etype != None:
				typ = e.etype.lower()
				if typ == 'birth':
					self.birth = e
				elif typ == 'death':
					self.death = e
				elif typ == 'marriage' or typ == 'partnership':
					self.partnerships.append(e)

	# Return an array containing the complete file contents
	#
	def GetTimeline(self):
		tl = []
		tl.append('======== Header ========')
		for ll in self.headlines:
			tl.append(ll)

		for e in self.events:
			tl.append('======== Event ========')
			for ll in e.lines:
				tl.append(ll)

		if len(self.footlines) > 0:
			tl.append('======== Footer ========')
			for ll in self.footlines:
				tl.append(ll)

		tl.append('')
		tl.append('======== Extracted data ========')
		tl.append('File = ' + str(self.filename))
		tl.append('Name = ' + self.name)
		tl.append('Uniq = [' + str(self.uniq) + ']')
		tl.append('Sex = ' + self.sex)
		if (self.birth == None ):
			tl.append('DoB = ?')
		else:
			tl.append('DoB = ' + self.birth.GetDate(0))
		for m in self.partnerships:
			print(m.date, m.etype, m.rest)
			tl.append(m.etype + '  ' + m.GetDate(0) + ' with ' + m.rest)
		if (self.death == None ):
			pass
		else:
			tl.append('DoD = '+self.death.GetDate(0))
		tl.append('Father = '+self.father_name+' ['+str(self.father_uniq)+']')
		tl.append('Mother = '+self.mother_name+' ['+str(self.mother_uniq)+']')
		return tl
