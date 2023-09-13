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
import re

from DhG_Config import Config
from DhG_Person import Person
from DhG_Event import Event

# A class to import a simple GEDCOM file
#
# Notes:
#	- A birth or death event in an INDI record should not have any text (other than Y) following the BIRT/DEAT tag
#	on the opening line. If there is such text, this importer treats it as a "Note" for the event.
#	- A death event with no additional attributes should have a Y after the opening DEAT tag. This importer
#	ignores that requirement and assumes a death at an unknown date.
#	- It isn't clear whether birth events follow the same rule. However, the mere existence of an individual
#	should be enough to infer a birth, even if there's no information. This importer automatically creates
#	a birth event for every individual, regardless of whether the gedcom has one.
#	- Dates are handled flexibly, assuming English text:
#		- Fields that exactly match months or reserved words like AFT, BEF etc. are handled as intended
#		- Other fields: 4 characters means year, 1 or 2 characters are day-of-month.
#	The result is that the fields can be in any order. For example JAN 1876 AFT 2 means exactly the same
#	as AFT 2 JAN 1876. Dates with a range (BET dd mmm yyyy AND dd mmm yyyy) are not supported yet.
#	- Date ranges FROM dd mmm yyyy TO dd mmm yyyy are similarly not processed. The gedcom spec warns against
#	using this form for events because it implies something that happened continuously over a period and thus
#	isn't an event. Unclear how things like military service are represented.
# 
class GedcomImporter():

	# Do the import in the constructor
	#
	#	ged		= gedcom file name
	#	db		= DhG database
	#
	def __init__(self, ged_name, db):
		self.db = db
		self.rec_start = 0
		self.persons = {}
		self.families = {}
		line_no = 0
		ged_file = open(ged_name, 'r')
		ged_text = ged_file.readlines()
		ged_file.close()
		ged_rec = []

		for l in ged_text:
			line_no += 1
			# Remove a byte-order marker if there is one. Usually on first line only
			if l[0] == '\ufeff':
#				print('BOM \\ufeff found')
				l = l[1:]
#			print('Line', l.rstrip())
			p = l.strip().split(' ', 1)
#			print('Parts', p)

			if p[0] == '0':
				# Start of a new record.
				self.rec_start = line_no

				# If there's already a record, process it
				if ged_rec != []:
					self.ProcessRecord(ged_rec)

				# Start a new record
				ged_rec = [l]

			elif ged_rec != []:
				ged_rec.append(l)

			else:
				print('Line '+str(line_no)+': "'+l.rstrip()+'" ignored; not part of a record')
				
		if ged_rec != []:
			self.ProcessRecord(ged_rec)

		return

	# Process a single (multi-line) record
	#
	#	ged_rec	= the record, as an array of lines
	#
	#	The reading process ensures that the first line of the record is at level 0
	#
	def ProcessRecord(self, ged_rec):
		p = ged_rec[0].strip().split(' ', 2)
		if p[1][0] == '@':
			tag = p[2]
		else:
			tag = p[1]
#		print('Record type', tag)
		if tag == 'HEAD':
			self.ProcessHead(ged_rec)
		elif tag == 'SUBM':
			self.ProcessSubm(ged_rec)
		elif tag == 'INDI':
			self.ProcessIndi(ged_rec)
		elif tag == 'FAM':
			self.ProcessFam(ged_rec)
		elif tag == 'NOTE':
			self.ProcessNote(ged_rec)
		elif tag == 'SOUR':
			self.ProcessSour(ged_rec)
		elif tag == 'TRLR':
			self.ProcessTrlr(ged_rec)
		else:
			print('ProcessRecord() line '+str(self.rec_start)+': record type "'+tag+'" ignored.')
#		print()
		return

	def ProcessHead(self, ged_rec):
#		print('ProcessHead()')
		return

	def ProcessSubm(self, ged_rec):
#		print('ProcessSubm()')
		return

	def ProcessIndi(self, ged_rec):
#		print('ProcessIndi()')
		p = ged_rec[0].strip().split(' ', 2)
		
		if p[1][0] == '@' and p[1][-1] == '@':
			xref = p[1]
#			print('ProcessIndi(): Xref = "'+xref+'"')
		else:
			print('Line '+str(self.rec_start)+': "'+ged_rec[0].rstrip()+'" has no Xref')
			return

		# Create the person object and populate the "headlines" array
		# Space is reserved for the following:
		#	0	- Name
		#	1	- Uniq
		#	2	- Male/Female
		#	3	- Father
		#	4	- Mother
		#	5	- Version:    2
		person = Person()
		person.headlines.append('')		# Name
		person.headlines.append('')		# Uniq
		person.headlines.append('')		# Male/Female
		person.headlines.append('')		# Father
		person.headlines.append('')		# Mother
		person.headlines.append('Version:    2')

		# Store the gedcom data and add the person to the list
		person.importer_info = GedcomInfo(ged_rec)
		person.importer_info.xref = xref
		self.persons[xref] = person

		# Assume that every person was born and add a Birth event.
		# Use a dedicated variable because more information might be coming along.
		birth_ev = Event()
		person.events.append(birth_ev)
		birth_ev.AddLine('?           Birth')

		l1 = None	# Tag of level 1 line
		ev = None	# Event object associated with the level 1 line
		grno = 0

		for l in ged_rec[1:]:
			grno += 1
			p =l.strip().split(' ', 2)
			if p[0] == '1':
				ev = None
				l1 = p[1]
				if l1 == 'NAME':
					if len(p) > 2:
						person.importer_info.name = p[2]
						person.headlines[0] = 'Name:       '+self.ConvertGedcomName(p[2])
					else:
						print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; no name given')
				elif l1 == 'SEX':
					if len(p) < 3:
						print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; no sex given')
					elif p[2] == 'M':
						person.headlines[2] = 'Male'
					elif p[2] == 'F':
						person.headlines[2] = 'Female'
					else:
						print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; sex not known')
				elif l1 == 'BIRT':
					# Recall the default birth record
					ev = birth_ev
					# Default Birth event has already been added.
					# If there's text (other than Y) on the line after BIRT, record it as a note.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Note       '+p[2])
				elif l1 == 'DEAT':
					# Add a Death event.
					ev = Event()
					person.events.append(ev)
					ev.AddLine('?           Death')
					# If there's text (other than Y) on the line after DEAT, record it as a note.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Note       '+p[2])
				elif l1 == 'FAMS':
					# Record families in which this person is a parent
					# This information might not be needed because each family record lists parents and children
					person.importer_info.fams.append(p[2])
				elif l1 == 'FAMC':
					# Record families in which this person is a child
					# This information might not be needed because each family record lists parents and children
					person.importer_info.famc.append(p[2])
				else:
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '2':
				if p[1] == 'DATE':
					if len(p) < 3:
						print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; no date given')
					elif ev == None:
						pass	# No event to add the date to
					else:
						date = self.ConvertGedcomDate(p[2])
						ev.lines[0] = date + ev.lines[0][len(date):]
				elif p[1] == 'PLAC':
					if len(p) < 3 and ev != None:
						ev.AddLine('+Place      '+p[2])
				else:
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			else:
				print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; level > 2')
		return

	def ProcessFam(self, ged_rec):
#		print('ProcessFam()')
		p = ged_rec[0].strip().split(' ', 2)
		
		if p[1][0] == '@' and p[1][-1] == '@':
			xref = p[1]
#			print('ProcessFam(): Xref = "'+xref+'"')
		else:
			print('Line '+str(self.rec_start)+': "'+ged_rec[0].rstrip()+'" has no Xref')
			return
		# Create a family record
		family = GedcomFamily(ged_rec)
		self.families[xref] = family

		for l in ged_rec[1:]:
			grno += 1
			p =l.strip().split(' ', 2)
			if p[0] == '1':
				l1 = p[1]
				if l1 == 'HUSB':
					family.husb = p[2]
				elif l1 == 'WIFE':
					family.wife = p[2]
				elif l1 == 'CHIL':
					family.chil.append(p[2])
				elif l1 == 'MARR':
					pass
				else:
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '2':
				l2 = p[2]
				if l2 == '_MREL' or l2 == '_FREL':
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; children assumed natural')
				else:
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored')
			else:
				print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; level > 2')
		return

	def ProcessNote(self, ged_rec):
#		print('ProcessNote()')
		return

	def ProcessSour(self, ged_rec):
#		print('ProcessSour()')
		return

	def ProcessTrlr(self, ged_rec):
#		print('ProcessTrlr()')
		return

	# Remove the surname indicators and any multiple spaces
	# Warn if the surname is not the last name element
	#
	def ConvertGedcomName(self, gedname):
		# Split the gedcom name into parts and remove duplicate spaces
		x = gedname.split(' ')
		parts = []
		for n in x:
			if n != '':
				parts.append(n)
		if parts[-1][0] == '/' and parts[-1][-1] == '/':
			# Family name is last - nothing to do
			pass
		else:
			# Family name is not last - handle this later
			print('Warning: in "'+gedname+'": family name is not last')
		return re.sub('/', '', ' '.join(parts))

	# Each part is either:
	#	a month
	#	a modifier
	#	a day or
	#	a year
	#
	def ConvertGedcomDate(self, geddate):
		parts = geddate.split(' ')
		mod = ''
		day = None
		month = None
		year = None
		for p in parts:
			if len(p) == 0:
				pass	# Ignore extra spaces
			elif p == 'JAN':
				month = '01'
			elif p == 'FEB':
				month = '02'
			elif p == 'MAR':
				month = '03'
			elif p == 'APR':
				month = '04'
			elif p == 'MAY':
				month = '05'
			elif p == 'JUN':
				month = '06'
			elif p == 'JUL':
				month = '07'
			elif p == 'AUG':
				month = '08'
			elif p == 'SEP':
				month = '09'
			elif p == 'OCT':
				month = '10'
			elif p == 'NOV':
				month = '11'
			elif p == 'DEC':
				month = '12'
			elif p == 'ABT':
				mod = '~'
			elif p == 'CAL':
				mod = '~'
			elif p == 'EST':
				mod = '~'
			elif p == 'BEF':
				mod = '<'
			elif p == 'AFT':
				mod = '>'
			elif p == 'BET':
				print('Warning: in date "'+geddate+'": BET not supported; using ABT <upper limit>')
				mod = '~'
			elif p == 'AND':
				pass	# Ignore AND (goes with BET)
			elif len(p) == 1:
				day = '0'+p
			elif len(p) == 2:
				day = '0'+p
			elif len(p) == 4:
				year = p
			else:
				print('Warning: in date "'+geddate+'": syntax not completely understood')

		if year == None:
			date = '?'
		else:
			date = year
			if month == None:
				pass
			else:
				date = date+'-'+month
				if day == None:
					pass
				else:
					date = date+'-'+day
			date = date+mod
		return date

# A class to hold extra GEDCOM information for a person
#
class GedcomInfo():

	def __init__(self, ged_rec):
		self.ged_rec = ged_rec
		self.xref = None
		self.name = None
		self.fams = []
		self.famc = []

# A class to hold a GEDCOM family
#
class GedcomFamily():

	def __init__(self, ged_rec):
		self.ged_rec = ged_rec
		self.xref = None
		self.husb = None
		self.wife = None
		self.chil = []
