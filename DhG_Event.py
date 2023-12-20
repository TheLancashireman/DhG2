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
from DhG_Template import T_Person, T_Event, T_EvInfo, T_Source, T_Transcript, T_File
import os
import traceback

# Event class - represents an event on a person's timeline
#
class Event:
	def __init__(self):
		self.lines = None
		self.owner = None
		self.date = None
		self.etype = None
		self.rest = None

	# Add a line of text to the event
	# The first line is the date and the event type
	#
	def AddLine(self, line):
		if self.lines == None:
			self.lines = [line]
			return
		self.lines.append(line)
		if line == '':
			return
		if line[0] == '#' or line[0] == '+' or line[0] == '-' or line[0] == '|':
			return
		print('Invalid form for event line: "'+line+'"')
		return

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
		etype = self.etype
		lctype = etype.lower()
		if lctype == 'marriage' or lctype == 'partnership':
			# Rest of event line is the partner
			(name, idx) = self.owner.ParseCombinedNameStringX(self.rest)
			if idx != None:
				tp = factory.db.GetTPerson(idx, 'yearonly')
			if tp == None:
				tp = T_Person(name, None)
		elif self.rest != None:
			if lctype == 'misc':
				etype = self.rest
			else:
				etype += ' ' + self.rest

		e = T_Event(self.GetDate('cooked'), etype, tp)

		# Now parse the rest of the lines
		i = 1
		self.nlines = len(self.lines)
		while i < self.nlines:
			line = self.lines[i].lstrip().rstrip()
			i += 1
			if line == '' or line[0] == '#' or line[0:5].lower() == '+todo':
				continue		# Ignore blanks, comments and todo
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
		if len(parts) < 2:
			evinfo = T_EvInfo(parts[0][1:], '')
		else:
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
					txt = line[1:]
					if txt != '':
						curinfo.info += ' ' + txt
			elif line[0] == '-':
				# Supplementary information
				parts = line.split(maxsplit=1)
				if parts[0].lower() == '-url':
					if len(parts) < 2:
						print('GetTEvInfo() warning: "'+line+'" no url provided. Ignored')
					else:
						evinfo.url = parts[1]
					curinfo = None			# No more continuation lines until next item
				elif parts[0].lower() == '-Uniq':
					# ToDo: the event info mentions a person in the database. This is the ID
					# The easy way will be to add a TPerson to the TEventInfo somehow
					# Just ignore for now.
					curinfo = None			# No more continuation lines until next item
				else:
					if len(parts) < 2:
						curinfo = T_EvInfo(parts[0][1:], '')
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
		curobj = None				# The object to add continuation lines to.
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
				if curobj == None:
					print('GetTSource warning: "'+line+'" nothing to continue. Ignored')
				else:
					txt = line[1:]
					if len(txt) > 1 and txt[0] == ' ':
						txt = txt[1:]
					curobj.AppendLine(txt)
			elif line[0:5].lower() == '-todo':
				pass	# Ignore ToDos
			elif line[0] == '-':
				curobj = None
				# Supplementary information
				parts = line.split(maxsplit=1)
				if parts[0].lower() == '-url':
					if len(parts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					src.AddRef('Link', parts[1])
				elif parts[0].lower() == '-file':
					if len(parts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					fparts = parts[1].split(maxsplit=1)
					if len(fparts) != 2:
						print('GetTSource() warning: "'+line+'" not recognised. Ignored')
						continue
					(ref, tref) = factory.AddFile(fparts[0], fparts[1])
					src.AddRef(ref, '#'+ref)
					if tref != None:
						src.AddRef(tref, '#'+tref)
				elif parts[0].lower() == '-transcript':
					if len(parts) >= 2:
						txt = parts[1]
					else:
						txt = ''
					(ref, curobj) = factory.AddTranscript(txt)
					src.AddRef(ref, '#'+ref)
				elif src.descr.lower() == 'personal knowledge' and (
							parts[0].lower() == '-of' or parts[0].lower() == '-from'):
					# Ignore "Personal knowledge" of/from - might be private
					pass
				else:
					if len(parts) >= 2:
						txt = parts[1]
					else:
						txt = ''
					curobj = T_EvInfo(parts[0][1:], txt)
					src.AddInfo(curobj)
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
	# Return a reference and the  T_Transcript() object. The latter allows adding text.
	#
	def AddTranscript(self, text):
		if self.transcripts == None:
			self.transcripts = [T_Transcript('T1', text)]
			return ('T1', self.transcripts[0])

		ref = 'T'+str(len(self.transcripts)+1)
		tx = T_Transcript(ref, text)
		self.transcripts.append(tx)
		return (ref, tx)

	# Add a transcript from a file to the list
	# Return a reference
	#
	def AddTranscriptFromFile(self, fname):
		(base, ext) = os.path.splitext(fname)
		if ext == '' or ext[0] != '.':
			return None
		if ext[1:] not in Config.Get('text-suffix').split(':'):
			return None

		fpath = Config.FindFile(fname, 'text_path', None)
		if fpath == None:
			print('File not found:', fname)
			return None

		try:
			f = open(fpath, 'r')
			content = f.readlines()
			text = ''.join(content)
			f.close
		except:
			print(traceback.format_exc())
			return None

		(ref, tx) = self.AddTranscript(text)
		return ref

	# Add a file to the list, if not already present
	# Return references to the file and its content (if file is a transcript file that can be handled)
	#
	def AddFile(self, ftype, fname):
		if self.files == None:
			self.files = []
		else:
			for fx in self.files:
				if fx.name == fname:
					# File is already in the list. Return its reference.
					if fx.ftype != ftype:
						print('AddFile() warning: "'+fname+'" referenced with different types')
					return (fx.ref, fx.tref)

		ref = 'F'+str(len(self.files)+1)
		fx = T_File(ref, ftype, fname)
		self.files.append(fx)

		if ftype.lower() == 'transcript':
			tref = self.AddTranscriptFromFile(fname)
			fx.tref = tref
		else:
			tref = None
		return (ref, tref)
