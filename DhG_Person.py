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
from DhG_Config import Config
from DhG_Event import Event
from DhG_Template import T_Person

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
		self.importer_info = None			# Used for storing extra information used by importers etc.

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

	# Parse a combined name/id string in the form 'Forename Name Lastname [id]'
	# Returns normalised name and id as a tuple.
	#
	# Implemented as a non-static to avoid a circular import. This is a nasty hack.
	#
	def ParseCombinedNameStringX(self, namestr):
		return Person.ParseCombinedNameString(namestr)

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


	# Returns DoB as a string
	#
	def GetDoB(self, fmt):
		if self.birth == None:
			return '?'
		return self.birth.GetDate(fmt)

	# Returns DoD as a string
	#
	def GetDoD(self, fmt):
		if self.death == None:
			return ''
		return self.death.GetDate(fmt)

	# Returns (DoB - DoD) as a string
	#
	def GetDates(self, fmt):
		return '(' + self.GetDoB(fmt) + ' - ' + self.GetDoD(fmt) + ')'

	# Return a string containing vital information about the person
	# fmt specifies what to return
	# datefmt spefies how to show dates
	#
	def GetVitalLine(self, fmt='display', datefmt='raw'):
		if fmt == 'card':	# cardfile format, e.g. Fred Bloggs [1234]
			idx_name = 0
			idx_uniq = 1
			idx_dates = -1
			parts = ['', '']
		else:				# display format, e.g. [1234] Fred Bloggs (1930-1969)
			idx_uniq = 0
			idx_name = 1
			idx_dates = 2
			parts = ['', '', '']

		if idx_uniq >= 0:
			if self.uniq == None:
				parts[idx_uniq] = '[?]'
			else:
				parts[idx_uniq] = '['+str(self.uniq)+']'

		if idx_name >= 0:
			if self.name == None:
				parts[idx_name] = 'not known'
			else:
				parts[idx_name] = self.name

		if idx_dates >= 0:
			dob = self.GetDoB(datefmt)
			dod = self.GetDoD(datefmt)
			parts[idx_dates] = '('+dob+' - '+dod+')'

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

	# Return a sorted list of partnership dates and partners
	#
	def GetPartners(self):
		if len(self.partnerships) == 0:
			return None

		p = []
		for m in self.partnerships:
			(sp_name, sp_uniq) = Person.ParseCombinedNameString(m.rest)
			t = (m.date, sp_uniq)
			p.append(t)
		p = sorted(p, key=lambda xx: xx[0])
		return p

	# Returns True if one or both parents is recorded in the database (not just as a name)
	#
	def HasParents(self):
		if  self.father_uniq == None and self.mother_uniq == None:
			return False
		return True

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
		tl.append('DoB = ' + self.GetDoB(None))
		for m in self.partnerships:
			tl.append(m.etype + '  ' + m.GetDate(None) + ' with ' + m.rest)
		if (self.death == None ):
			pass
		else:
			tl.append('DoD = '+self.GetDoD(None))
		if self.father_name != None:
			tl.append('Father = '+self.father_name+' ['+str(self.father_uniq)+']')
		if self.mother_name != None:
			tl.append('Mother = '+self.mother_name+' ['+str(self.mother_uniq)+']')
		return tl

	# Return a T_Person object the person
	#
	def GetTPerson(self, dateformat):
		fn = Config.MakePersonfileName(self.name, self.uniq,
						prefix = '',
						suffix='', surname_dir=True)
		tp = T_Person(self.name, self.uniq,
						dob_dod = self.GetDates(dateformat),
						file = fn)
		# tp.other left at default; must be added later if needed
		return tp
