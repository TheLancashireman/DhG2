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
# This class is developed to import a GEDCOM file from Family Tree Maker (FTM), specifically
# a genealogy from the Dobbs report related to the Hutchinson bequest (Co. Antrim).
# Some of the syntax and semantics in that file are questionable to say the least. I don't know
# whether that is because of the dataset itself or a characteristic of FTM generally.
#
# Notes:
#	- A birth or death event in an INDI record should not have any text (other than Y) following the BIRT/DEAT tag
#	on the opening line. If there is such text, this importer treats it as a "Note" for the event.
#	- A death event with no additional attributes should have a Y after the opening DEAT tag. This importer
#	ignores that requirement and assumes a death at an unknown date.
#	- It isn't clear whether birth events follow the same rule. However, the mere existence of an individual
#	- A MARR event (usually in a FAM object) should similarly have either Y or nothing. This importer adds
#	any additional text as a Note for the event. In some cases it looks a bit strange.
#	should be enough to infer a birth, even if there's no information. This importer automatically creates
#	a birth event for every individual, regardless of whether the gedcom has one.
#	- Dates are handled flexibly, assuming English text:
#		- Fields that exactly match months or reserved words like AFT, BEF etc. are handled as intended
#		- Other fields: 4 characters means year, 1 or 2 characters are day-of-month.
#	The result is that the fields can be in any order. For example JAN 1876 AFT 2 means exactly the same
#	as AFT 2 JAN 1876. Events with a dates range (BET dd mmm yyyy AND dd mmm yyyy) are recorded as
#	AFT <first date> with a qualifer '+Before <second date>. That keeps the ordering correct (I hope).
#	- Date ranges FROM dd mmm yyyy TO dd mmm yyyy are similarly not processed. The gedcom spec warns against
#	using this form for events because it implies something that happened continuously over a period and thus
#	isn't an event. Unclear how things like military service are represented.
#
#	From GEDCOM551.pdf:
#		CONT means concatenate the text with the previous text with a newline between.
#		CONC means concatenate the text with the previous text without any white space.
#	Seems only to be used in NOTE objects.


class GedcomImporter():

	# Do the import in the constructor
	#
	#	ged		= gedcom file name
	#	db		= DhG database
	#
	def __init__(self, ged_name, db):
		# The DhG2 memory-resident database that we're importing into.
		self.db = db

		# Gedcom records. Each record starts with a level 0 line
		self.head = None		# Single record. Are we interested in this?
		self.subm = None		# Single record. Are we interested in this?
		self.indi = {}			# Multiple records. Each should have an xref to identify it
		self.fam = {}			# Multiple records. Each should have an xref to identify it
		self.note = {}			# Multiple records. Each should have an xref to identify it
		self.sour = {}			# Multiple records. Each should have an xref to identify it
		self.trlr = None		# Single record. Are we interested in this?

		self.persons = {}		# A list of all the persons in the database, indexed by xref
		self.indiref_ok = True	# All INDI xrefs are of the form @In@
		self.max_uniq = 0		# Largest uniq in the gedcom

		# Read the file and split up into individual records
		self.ReadFile(ged_name)

		# Process all the INDI records and add persons to the database
		for i in self.indi:
			self.ProcessIndi(self.indi[i])

		# Add individuals whose xref isn't the standard form
		if not self.indiref_ok:
			self.AllocateNonstandardIndividuals()

		# Connect all the persons together using the FAM records
		for f in self.fam:
			self.ProcessFam(self.fam[f])

		# Reprocess the header for each person. This will overwrite some of the previously
		# calculated stuff, but it should be the same.
		# Append death event to event list for each person in GEDCOM
		# ProcessIndi creates a death event if present in GEDCOM, but doesn't add it to the
		# person's list, in order to ensure that the death comes last.
		for pref in self.persons:
			p = self.persons[pref]
			p.AnalyseHeader()
			if p.death == None:		# Special for Dobbs: all individuals assumed dead. If no death record, add one
				p.death = Event()
				p.death.AddLine('?           Death')
				p.death.AddLine('+Source     Assumed, date unknown')
				p.death.DecodeEventType(p)
			p.events.append(p.death)	# Death record is always last
		return

	# Read the GEDCOM file and split into different record objects
	#
	def ReadFile(self, ged_name):
		line_no = 0
		ged_file = open(ged_name, 'r')
		ged_text = ged_file.readlines()
		ged_file.close()
		ged_obj = None

		for l in ged_text:
			line_no += 1
			# Remove a byte-order marker if there is one. Usually on first line only
			if l[0] == '\ufeff':
				l = l[1:]
			p = l.strip().split(' ', 1)

			if p[0] == '0':
				# If there's already an object, add it to the lists
				if ged_obj != None:
					self.AddGedObj(ged_obj)

				# Start of a new object.
				ged_obj = GedObject(line_no, l)

			elif ged_obj != None:
				ged_obj.AddLine(l)

			else:
				print('Line '+str(line_no)+': "'+l.rstrip()+'" ignored; not part of a record')

		# This is most likely to be the TRLR record
		if ged_obj != None:
			self.AddGedObj(ged_obj)

		return

	# Add a single object to one of the lists
	#
	#	obj	= the record containing an array of lines and other items
	#
	#	The reading process ensures that the first line of the record is at level 0
	#
	def AddGedObj(self, obj):
		tag = obj.tag
		if tag == 'HEAD':
			if self.head == None:
				self.head = obj
			else:
				print('Repeat HEAD record in line '+str(obj.first_line)+' ignored')
		elif tag == 'SUBM':
			if self.subm == None:
				self.subm = obj
			else:
				print('Repeat SUBM record in line '+str(obj.first_line)+' ignored')
		elif tag == 'TRLR':
			if self.trlr == None:
				self.trlr = obj
			else:
				print('Repeat TRLR record in line '+str(obj.first_line)+' ignored')
		elif tag == 'INDI':
			if obj.xref == None:
				print('INDI record with no xref in line '+str(obj.first_line)+' ignored')
			else:
				self.indi[obj.xref] = obj
		elif tag == 'FAM':
			if obj.xref == None:
				print('FAM record with no xref in line '+str(obj.first_line)+' ignored')
			else:
				self.fam[obj.xref] = obj
		elif tag == 'NOTE':
			if obj.xref == None:
				print('NOTE record with no xref in line '+str(obj.first_line)+' ignored')
			else:
				self.note[obj.xref] = obj
		elif tag == 'SOUR':
			if obj.xref == None:
				print('SOUR record with no xref in line '+str(obj.first_line)+' ignored')
			else:
				self.sour[obj.xref] = obj
		else:
			print('Record with unknown tag "'+tag+' in line '+str(obj.first_line)+' ignored')
#		print()
		return

	# Insert an event into the event list in sorted order
	# Birth is assumed to be event[0], death is appended afterwards, so is always last.
	# '?' is greater than all digits, so events with unknown dates come after those with known dates
	#
	def InsertEvent(self, list, event):
		for i in range(1, len(list)):
			if list[i].date > event.date:
				list.insert(i, event)
				return
		list.append(event)

	# Process an INDI record. Add a person to the database and fill with all relevant information
	#
	def ProcessIndi(self, obj):
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
		person.headlines.append('')		# Blank line

		# Store the gedcom data and add the person to the list
		person.importer_info = GedcomInfo(obj)
		self.persons[obj.xref] = person

		# Calculate a uniq from the xref, if possible
		person.uniq = self.ExtractUniqFromXref(obj.xref)
		if person.uniq != None:
								#  123456789012
			person.headlines[1] = 'Uniq:       '+str(person.uniq)
#			print(person.headlines[1])
			self.db.AddPerson(person.uniq, person)
			if person.uniq > self.max_uniq:
				self.max_uniq = person.uniq

		# Assume that every person was born and add a Birth event.
		ev = Event()
		ev.AddLine('?           Birth')
		ev.DecodeEventType(person)
		person.birth = ev
		person.events.append(ev)

		l1 = None	# Tag of level 1 line
		ev = None	# Event object associated with the level 1 line
		grno = 0

		for l in obj.lines[1:]:
			grno += 1
			p =l.strip().split(' ', 2)
			if p[0] == '1':
				ev = None
				l1 = p[1]
				if l1 == 'NAME':
					if len(p) > 2:
						person.importer_info.name = p[2]
						n = self.ConvertGedcomName(p[2])
						person.name = n
											#  123456789012
						person.headlines[0] = 'Name:       '+n
					else:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; no name given')
				elif l1 == 'SEX':
					if len(p) < 3:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; no sex given')
					elif p[2] == 'M':
						person.headlines[2] = 'Male'
						person.sex = 'm'
					elif p[2] == 'F':
						person.headlines[2] = 'Female'
						person.sex = 'f'
					elif p[2] == 'U':		# Special for Dobbs: most seem to be male
						person.headlines[2] = 'Male'
						person.sex = 'm'
					else:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; sex not known')
				elif l1 == 'EVEN':
					# This appears to be a remark about the name of the person
					# See TYPE at L2         123456789012
					person.headlines.append('Note:       '+p[2])
				elif l1 == 'BIRT':
					# Recall the default birth record
					ev = person.birth
					# Default Birth event has already been added.
					# If there's text (other than Y) on the line after BIRT, record it as a note.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Note       '+p[2])
				elif l1 == 'EMIG':
					# Add a Travel event.
					# Special for Dobbs
					ev = Event()
					self.InsertEvent(person.events, ev)
					ev.AddLine('?           Emigration')
					# If there's text on the line after EMIG, record it as the destination.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Where      '+p[2])
					ev.DecodeEventType(person)
				elif l1 == 'PROP':
					# Add a miscellaneous event for property acquisition.
					# Special for Dobbs
					ev = Event()
					self.InsertEvent(person.events, ev)
					ev.AddLine('?           Misc        Property acquisition')
					# If there's text on the line after PROP, record it as a note.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Note       '+p[2])
					ev.DecodeEventType(person)
				elif l1 == 'OCCU':
					# Add a miscellaneous event for occupation
					# Special for Dobbs
					ev = Event()
					self.InsertEvent(person.events, ev)
					ev.AddLine('?           Misc        Occupation')
					# If there's text on the line after OCCU, record it as occupation AND ass a header line
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Occupation '+p[2])
						person.headlines.append('Occupation: '+p[2])
					ev.DecodeEventType(person)
				elif l1 == 'DEAT':
					# Add a Death event, but don't append to the list yet.
					ev = Event()
					person.death = ev
					ev.AddLine('?           Death')
					# If there's text (other than Y) on the line after DEAT, record it as a note.
					if len(p) > 2 and p[2] != 'Y':
						ev.AddLine('+Note       '+p[2])
					ev.DecodeEventType(person)
				elif l1 == 'NOTE':
					# Add a note to the header lines
					try:
						note = self.note[p[2]]
					except:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": referenced note not found')
						note = None
					if note != None:
						person.headlines += self.ProcessNote(note, 'h')
				elif l1 == 'FAMS':
					# Record families in which this person is a parent
					# This information might not be needed because each family record lists parents and children
					person.importer_info.fams.append(p[2])
				elif l1 == 'FAMC':
					# Record families in which this person is a child
					# This information might not be needed because each family record lists parents and children
					person.importer_info.famc.append(p[2])
				else:
					print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '2':
				l2 = p[1]
				if l2 == 'DATE':
					if len(p) < 3:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; no date given')
					elif ev == None:
						pass	# No event to add the date to
					else:
						(date, date1) = self.ConvertGedcomDate(p[2])
						ev.date = date
						ev.lines[0] = date + ev.lines[0][len(date):]
						if date1 != None:
							ev.lines.insert(1, '+Before     '+date1)
				elif l2 == 'PLAC':
					if ev != None:
						if len(p) > 2:
							ev.AddLine('+Place      '+p[2])
						else:
							ev.AddLine('+Place      not given')
				elif l2 == 'TYPE':
					if l1 == 'EVEN':
						if p[2] != 'Surname' and p[2] != 'Family Genealogy':
							print('Warning: previous EVEN line has "TYPE '+p[2]+'". Expected "Surname"')
				elif l2 == 'SOUR':
					try:
						source = self.sour[p[2]]
					except:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": referenced source not found')
						source = None
					if source != None:
						sourcelines = self.ProcessSource(source)
						if ev == None:
							print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": no event for referenced source')
						else:
							ev.lines += sourcelines
				else:
					print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '3':
				l3 = p[1]
				if l2 == 'PLAC' and l3 == 'MAP':
					if ev == None:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; MAP tag with no event')
					else:
						ev.AddLine('-Mapref')
						if len(p) > 2:
							print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored unexpected data')
				elif l2 == 'SOUR' and l3 == 'PAGE':
					if len(p) < 3 or p[2] == '':
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; PAGE tag with no data')
					elif ev == None:
						print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; PAGE tag with no event')
					else:
								#   123456789012
						ev.AddLine('-Page       ' + p[2])
				else:
					print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '4':
				l4 = p[1]
				if l3 == 'MAP' and l4 == 'LATI' or l4 == 'LONG':
					if ev.lines[-1] == '-Mapref':
						ev.lines[-1] = ev.lines[-1] + '     ' + p[2]
					else:
						ev.lines[-1] = ev.lines[-1] + ' ' + p[2]
				else:
					print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			else:
				print('Line '+str(obj.first_line+grno)+' "'+l.rstrip()+'": ignored; level > 4')
		return

	# Create a DhG note from a GEDCOM NOTE object.
	#	The result is an array of lines of text in one of three styles:
	#		h - for the person's heading lines. Startes with "Note:"
	#		e - for an event. Starts with "+Note"
	#		s - subsidiary to an event attribute. Starts with "-Note"
	#	If the note is a single-line note, the "starts with" is padded to 12 chars and the text added on the same line.
	#	If the note is a multi-line note, the "starts with" is on a line of its own and eack line of text is added as
	#	a continuation line starting with "| ".
	#
	def ProcessNote(self, note, style):
		# Text of note.
		text = []
		multiline = False
		grno = 0

		for l in note.lines[1:]:
			grno += 1
			p = l.strip().split(' ', 2)
			if p[0] == '1':
				if p[1] == 'CONT':
					# Concatenate with newline. See comment at top of file
					# In DhG, multi-line notes usa a continuation indicator "| "
					if len(p) < 3:
						text.append('|')			# Empty continuation line
					else:
						 text.append('| ' + p[2])	# Continuation line with text
					multiline = True
				elif p[1] == 'CONC':
					# Concatenate without newline. See comment at top of file
					# The text is concatenated onto the last element of the text array,
					# with a space if the last element was only a continuation character
					if len(p) < 3:
						pass		# Nothing to concatenate
					elif len(text) <= 0:
						text.append(p[2])
					elif text[-1] == '|':
						text[-1] += ' ' + p[2]
					else:
						text[-1] += p[2]
				else:
					print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			else:
				print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; level > 1')

		if multiline:
			# Insert the Note specifier in the selected style.
			if style == 'h':
				text.insert(0, 'Note:')
			elif style == 'e':
				text.insert(0, '+Note')
			elif style == 's':
				text.insert(0, '-Note')
			else:
				return []
			# Ensure that the first line of text has a continuation marker
			if text[1] == '':
				text[1] = '|'
			elif text[1][0] != '|':
				text[1] = '| '+text[1]
		else:
			# Insert the Note specifier in the selected style.
			if style == 'h':
				text[0] = 'Note:       ' + text[0]
			elif style == 'e':
				text[0] = 0, '+Note       ' + text[0]
			elif style == 's':
				text[0] = 0, '-Note       ' + text[0]
			else:
				return []

#		print('ProcessNote(): style', style, 'multiline', multiline)
#		print(note.lines)
#		print(text)
		return text

	# Create a DhG Source attribute from a GEDCOM SOUR object.
	# The resulting attribute is a list of lines of text looking like this:
	#	123456789012
	#	+Source     TITL
	#	-Author     AUTH
	#	-Edition    PUBL
	#	-Note
	#	| NOTE
	#
	# The usual -File, -URL -Transcript etc. could be added later if found in other GEDCOM files.
	# Dobbs has only one SOUR object.
	def ProcessSource(self, sour):
		source = ['+Source     ']
		grno = 0

		for l in sour.lines[1:]:
			grno += 1
			p = l.strip().split(' ', 2)
			if len(p) < 3:
				txt = ''
			else:
				txt = p[2]
			if p[0] == '1':
				l1 = p[1]
				if l1 == 'TITL':
					# Append to the source line.
					if source[0] == '+Source     ':
						source[0] += txt
					else:
						source[0] += ' ' + txt
				elif l1 == 'AUTH':
								#  123456789012
					source.append('-Author     ' + txt)
				elif l1 == 'PUBL':
								#  123456789012
					source.append('-Edition    ' + txt)
				elif l1 == 'NOTE':
								#  123456789012
					source.append('-Note       ' + txt)
				else:
					print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; unrecognised tag')
			elif p[0] == '2':
				l2 = p[1]
				if l1 == 'NOTE':
					if l2 == 'CONT' or l2 == 'CONC':
						if txt == '':
							source.append('|')
						else:
							source.append('| ' + txt)
					else:
						print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; unrecognised tag')
				else:
					print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; unexpected line at L2')
			else:
				print('Line '+str(note.first_line+grno)+' "'+l.rstrip()+'": ignored; level > 2')

		return source

	# If there are any individuals whose xref is not in the standard @In@ form,
	# this function is called.
	# The intention is to add them to the database with uniq upwards of the highest
	#
	def AllocateNonstandardIndividuals(self):
		print('Warning: there are individuals whose xref is not the standard form.')
		for pi in self.persons:
			p = self.persons[pi]
			if p.uniq == None:
				self.max_uniq += 1
				p.uniq = self.max_uniq
								# 123456789012
				p.headlines[1] = 'Uniq:       '+str(p.uniq)
				self.db.AddPerson(p.uniq, p)
		return

	# Connect the families by adding HUSB and WIFE from each FAM record as father and mother
	# of each CHIL listed in the FAM record. Also add marriage event (if present) to the HUSB and WIFE
	#
	# An interesting conundrum here:
	# There's a two-way relationship between persons and families, because each INDI
	# has a FAMS (family in which person is a spouse) and FAMC (family in which person is a child).
	# It is possible to ignore the FAM records and just use the references in the INDI records.
	# Similarly it is possible to ignore the FAMS/FAMC attributes and just use the FAM records. The
	# latter has the advantage that perhaps it's possible to infer the sex of an individual
	# who is a HUSB or WIFE in a FAM record.
	# This function ignores the FAMS/FAMC lists.
	#
	# It would be possible to use the bidirectional relationships as a check; we won't go there yet.
	# What if an individual is listed as a child in two families? Answer: there were a few; all were errors
	# in the gedcom.
	#
	def ProcessFam(self, family):
		husb = None
		wife = None
		marr = None		# Marriage date: None ==> no record, '?' ==> no date, else date
		mar1 = None		# Marriage date: later limit
		plac = None		# Marriage place
		mapr = None		# Marriage map reference
		mnot = None		# Marriage note (extra text on MARR line)
		chil = []		# List of children

		l1 = None	# Tag of level 1 line
		grno = 0

		# Read and process all the lines from the family object
		for l in family.lines[1:]:
			grno += 1
			p =l.strip().split(' ', 2)
			if p[0] == '1':
				l1 = p[1]
				if l1 == 'HUSB':
					husb = p[2]
				elif l1 == 'WIFE':
					wife = p[2]
				elif l1 == 'CHIL':
					chil.append(p[2])
				elif l1 == 'MARR':
					marr = '?'
					if len(p) > 2 and p[2] != 'Y':
						mnot = p[2]
				else:
					print('Line '+str(self.rec_start+grno)+' "'+l.rstrip()+'": ignored; unknown tag')
			elif p[0] == '2':
				l2 = p[1]
				if l2 == '_MREL' or l2 == '_FREL':
					if p[2] != 'Natural':
						print('Line '+str(family.first_line+grno)+' "'+l.rstrip()+'": ignored; children assumed natural')
				elif l2 == 'DATE' and l1 == 'MARR':
					(marr, mar1) = self.ConvertGedcomDate(p[2])
				elif l2 == 'PLAC' and l1 == 'MARR':
					plac = p[2]
				else:
					print('Line '+str(family.first_line+grno)+' "'+l.rstrip()+'": ignored')
			elif p[0] == '3':
				l3 = p[1]
				if l3 == 'MAP':
					pass
				else:
					print('Line '+str(family.first_line+grno)+' "'+l.rstrip()+'": ignored')
			elif p[0] == '4':
				l4 = p[1]
				if l3 == 'MAP' and l4 == 'LATI' or l4 == 'LONG':
					if mapr == None:
						mapr = p[2]
					else:
						mapr += ' ' + p[2]
				else:
					print('Line '+str(family.first_line+grno)+' "'+l.rstrip()+'": ignored')
			else:
				print('Line '+str(family.first_line+grno)+' "'+l.rstrip()+'": ignored; level > 4')

		if husb == None:
			father = None
		else:
			try:
				father = self.persons[husb]
							 # 123456789012
			except:
				print('Warning: HUSB '+husb+' not found in database')
				father = None
		if father == None:
						#  123456789012
			father_line = 'Father:     not known'
		else:
						#  123456789012
			father_line = 'Father:     '+father.name+' ['+str(father.uniq)+']'

		if wife == None:
			mother = None
		else:
			try:
				mother = self.persons[wife]
							 # 123456789012
			except:
				print('Warning: WIFE '+wife+' not found in database')
				mother = None
		if mother == None:
						#  123456789012
			mother_line = 'Mother:     not known'
		else:
						#  123456789012
			mother_line = 'Mother:     '+mother.name+' ['+str(mother.uniq)+']'

		for c in chil:
			try:
				child = self.persons[c]
			except:
				print('Warning: CHIL '+c+' not found in database')
				child = None
			if child != None:
				if child.headlines[3] == '' and child.headlines[4] == '':
					if father != None:
						child.headlines[3] = father_line
						child.father_name = father.name
						child.father_uniq = father.uniq
					if mother != None:
						child.headlines[4] = mother_line
						child.mother_name = mother.name
						child.mother_uniq = mother.uniq
				else:
					print('Warning:', child.name, '['+str(child.uniq)+'] (', c, ') has two sets of parents:')
					print('   Existing: ', child.headlines[3])
					print('             ', child.headlines[4])
					print('   Found:    ', father_line)
					print('             ', mother_line)

		# Special for Dobbs - assume a marriage took place
		if marr == None:
			marr = '?'

		if marr != None:
			el0 = marr
			for i in range(len(marr), 12):
				el0 += ' '
			el0 += 'Marriage    '
			elines = ['']
			if mar1 != None:
							#  123456789012
				elines.append('+Before     '+mar1)
			if mnot != None:
							#  123456789012
				elines.append('+Note       '+mnot)
			if plac != None:
							#  123456789012
				elines.append('+Place      '+plac)
				if mapr != None:
								#  123456789012
					elines.append('-Mapref     '+mapr)

			if father != None:
				ev = Event()
				if mother == None:
					elines[0] = el0 + 'not known'
				else:
					elines[0] = el0 + mother.GetVitalLine(fmt='card')
				if ev.lines == None:
					ev.lines = elines
				else:
					ev.lines += elines
				ev.DecodeEventType(father)
				self.InsertEvent(father.events, ev)
				father.partnerships.append(ev)

			if mother != None:
				ev = Event()
				if father == None:
					elines[0] = el0 + 'not known'
				else:
					elines[0] = el0 + father.GetVitalLine(fmt='card')
				if ev.lines == None:
					ev.lines = elines
				else:
					ev.lines += elines
				ev.DecodeEventType(mother)
				self.InsertEvent(mother.events, ev)
				mother.partnerships.append(ev)
		return

	# Remove the surname indicators and any multiple spaces
	# Warn if the surname is not the last name element
	#
	def ConvertGedcomName(self, gedname):
		# Split the gedcom name into parts and remove duplicate spaces
		x = gedname.split(' ')
		parts = []
		extra = []
		found_surname = False
		for n in x:
			if n == '':
				pass		# Ignore empty parts
			elif found_surname:
				extra.append(n)
			else:
				if n[0] == '/' and n[-1] == '/':
					found_surname = True
					n = n[1:-1]
				parts.append(n)
		if len(extra) != 0:
			# Family name is not last
			print('Warning: in "'+gedname+'": family name is not last')
			# Put all remaining parts in brackets before the family name
			# Dobbs special: this is a hack for names like "Joe Bloggs Sr."
			parts.insert(-1, '('+' '.join(extra)+')')
			print('ConvertGedname(): Name is', ' '.join(parts))
		elif not found_surname:
			# Explicit family name not found
			print('Warning: in "'+gedname+'": family name not found. Last name will be family name as usual')
		return ' '.join(parts)

	# Extract an integer from an INDI xref
	# Warn and return None if the xref is not of the form @Id...d@
	#
	def ExtractUniqFromXref(self, xref):
		# Check the non-digit characters
		if xref[0] == '@' and xref[1] == 'I' and xref[-1] == '@':
			try:
				uniq = int(xref[2:-1], 10)
				if uniq <= 0:
					uniq = None
			except:
				uniq = None
		else:
			uniq = None

		if uniq == None:
			print('Warning: "'+xref+'": not in expected form')
			self.indiref_ok = False
		return uniq

	# Construct a date out of component parts, some of which might not exist
	#
	def BuildDate(self, year, month, day, mod):
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
		date0 = None
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
				date0 = self.BuildDate(year, month, day, '>')
				year = None
				month = None
				day = None
			elif p == 'AND':
				pass	# Ignore AND (goes with BET)
			elif len(p) == 1:
				day = '0'+p
			elif len(p) == 2:
				day = p
			elif len(p) == 4:
				year = p
			else:
				print('Warning: in date "'+geddate+'": syntax not completely understood')

		date = self.BuildDate(year, month, day, mod)
		if date0 == None:
			return (date, None)
		else:
			return (date0, date)

#	A representation of a record from the GEDCOM file.
#
class GedObject():
	def __init__(self, first_line, line0):
		self.first_line = first_line	# The line number in the file that contains the level 0 record
		self.lines = [line0]			# An array holding all the lines in the record
		self.tag = None					# The record type
		self.xref = None				# The xref to identify the record

		p = line0.strip().split(' ', 2)	# Extract the tag and (optional) identifier from the level 0 line
		if p[1][0] == '@':
			self.xref = p[1]
			self.tag = p[2]
		else:
			self.tag = p[1]
		return

	def AddLine(self, line):
		self.lines.append(line)
		return

# A class to hold extra GEDCOM information for a person
#
class GedcomInfo():
	def __init__(self, obj):
		self.obj = obj
		self.name = None
		self.fams = []
		self.famc = []
