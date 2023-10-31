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

from DhG_Config import Config
from DhG_Template import T_Event, T_EvInfo, T_Source, T_Transcript, T_File

# Event class - represents an event on a person's timeline
#
class Event:
	def __init__(self):
		self.lines = []
		self.owner = None
		self.date = None
		self.etype = None
		self.rest = None

	# Add a line of text to the event
	# The first line is the date and the event type
	#
	def AddLine(self, line):
		self.lines.append(line)

	# Decode the first line of the event
	#
	def DecodeEventType(self, owner):
		self.owner = owner
		parts = self.lines[0].split(maxsplit=2)
		try:
			self.date = parts[0]
			self.etype = parts[1]
		except:
			print('Insufficient fields in event date line', self.lines[0], 'in', owner.filename)

		if len(parts) > 2:
			self.rest = parts[2]
		return

	# Return the date in the specified format
	#
	def GetDate(self, fmt):
		return Config.FormatDate(self.date, None, fmt)

	# Return a T_Event structure for templates
	#
	def GetTEvent(self, factory):
		# Create the basic T_Event structure
		tp = None
		lctype = self.etype.lower()
		if lctype == 'marriage' or lctype == 'partnership':
			# Rest of event line is the partner
			(name, idx) = self.owner.ParseCombinedNameStringX(self.rest)
			if idx != None:
				tp = factory.db.GetTPerson(idx, 'yearonly')
			if tp == None:
				tp = TPerson(name, None)

		e = T_Event(self.GetDate('cooked'), self.etype, tp)

		# Now parse the rest of the lines
		i = 1
		self.nlines = len(self.lines)
		while i < self.nlines:
			line = self.lines[i].lstrip().rstrip()
			i += 1
			if line == '' or line[0] == '#':
				continue		# Ignore blanks and comments
			if line[0] == '+':
				parts = line.split(maxsplit=1)
				if parts[0].lower() == '+source':
					(i, src) = self.GetTSource(factory, parts, i)
					e.sources.append(src)
				else:
					# Event information
					(i, ei) = self.GetTEvInfo(parts, i)
					e.information.append(ei)
			else:
				# Line not starting with + found at outer level :-(
				print('GetTEvent() warning: "'+line+'" found at top level. Ignored')
		return e

	# Return a T_EvInfo object and the index of the line after the info
	#
	def GetTEvInfo(self, parts, i):
		evinfo = T_EvInfo(parts[0][1:], parts[1])
		curinfo = evinfo
		while i < self.nlines:
			line = self.lines[i]
			i += 1
			if line == '' or line[0] == '#':
				continue		# Ignore blanks and comments
			if line[0] == '+':
				# Next item
				return (i-1, evinfo)
			if line[0] == '|':
				# Continuation character
				if curinfo == None:
					print('GetTEvInfo() warning: "'+line+'" nothing to continue. Ignored')
				else:
					txt = line[1:].lstrip()
					if txt != '':
						curinfo.info += ' ' + txt
			elif line[0] == '-':
				# Supplementary information
				parts = line.split(maxsplit=1)
				if parts[0].lower() == '-url':
					evinfo.url = parts[1]
					curinfo = None			# No more continuation lines until next item
				else:
					curinfo = T_EvInfo(parts[0][1:], parts[1])
					evinfo.AddInfo(curinfo)
			else:
				print('GetTEvInfo() warning: "'+line+'" not recognised. Ignored')

		return (i, evinfo)

	# Return a T_Source object and the index of the line after the source block
	#
	def GetTSource(self, factory, parts, i):
		src = T_Source(parts[1])
		tx = None
		while i < self.nlines:
			line = self.lines[i]
			i += 1
			if line == '' or line[0] == '#':
				continue		# Ignore blanks and comments
			if line[0] == '+':
				# Next item
				return (i-1, src)
			if line[0] == '|':
				# Continuation character
				if tx == None:
					print('GetTSource warning: "'+line+'" nothing to continue. Ignored')
				else:
					txt = line[1:].lstrip()
					if txt != '':
						tx.AppendLine(txt)
			elif line[0] == '-':
				tx = None
				# Supplementary information
				parts = line.split(maxsplit=1)
				if parts[0].lower() == '-url':
					if len(parts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					src.AddRef(('Link', parts[1]))
				elif parts[0].lower() == '-file':
					if len(parts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					fparts = parts[1].split(maxsplit=1)
					if len(fparts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					ref = factory.AddFile(fparts[0], fparts[1])
					src.AddRef((ref, '#'+ref))
				elif parts[0].lower() == '-transcript':
					if len(parts) >= 2:
						txt = parts[1]
					else:
						txt = ''
					(ref, tx) = factory.AddTranscript(txt)
					src.AddRef((ref, '#'+ref))
				else:
					print('GetTSource() warning: "'+line+'" not recognised. Ignored')
			else:
				print('GetTSource() warning: "'+line+'" not recognised. Ignored')
		return (i, src)

# A class to create a list of T_Event objects for a template,
# along with the associated list of T_Transcript and T_File objects
#
class TEventFactory():
	def __init__(self, db):
		self.db = db
		self.events = None		# List of T_Event objects
		self.transcripts = None	# List of T_Transcript objects
		self.files = None		# List of T_File objects
		return

	# Process an event ad add its contents to the lists
	#
	def AddEvent(self, ev):
		tev = ev.GetTEvent(self)
		if self.events == None:
			self.events = [tev]
		else:
			self.events.append(tev)
		return

	# Add a transcript to the list
	# Return a reference and the reference
	#
	def AddTranscript(self, text):
		if self.transcripts == None:
			self.transcripts = [T_Transcript('T1', text)]
			return ('T1', self.transcripts[0])

		ref = 'T'+str(len(self.transcripts)+1)
		tx = T_Transcript(ref, text)
		self.transcripts.append(tx)
		return (ref, tx)

	# Add a file to the list, if not already present
	# Return a reference to the file
	#
	def AddFile(self, ftype, fname):
		if self.files == None:
			self.files = [T_File('F1', ftype, fname)]
			return 'F1'

		for fx in self.files:
			if fx.name == fname:
				# File is already in the list. Return its reference.
				if fx.ftype != ftype:
					print('AddFile() warning: "'+fname+'" referenced with different types')
				return fx.ref

		ref = 'F'+str(len(self.transcripts)+1)
		self.files.append(T_File(ref, ftype, fname))
		return ref
