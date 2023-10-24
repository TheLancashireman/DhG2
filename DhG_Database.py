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
from pathlib import Path
from DhG_Config import Config
from DhG_Person import Person
from DhG_Template import T_Person
from DhG_GedcomImporter import GedcomImporter

# A class to represent the entire database
#
# The persons in the database are stored in an array indexed by the unique ID
# The order in which the elements arrice is not known, so the gaps in the array are filled
# with None as the loading proceeeds.
#
class Database:
	def __init__(self, basepath):
		self.persons = []
		self.basepath = basepath
		self.mf = {}				# Male or female per name

	# Add a person to the database, after expanding the array to ensure that the entry exists.
	#
	def AddPerson(self, uniq, person):
		while len(self.persons) <= uniq:
			self.persons.append(None)

		if self.persons[uniq] == None:
			self.persons[uniq] = person
		else:
			print('Error: id', uniq, 'is not unique')

	# Reload the entire database
	#
	def Reload(self):
		self.persons = []
		self.mf = {}
		for path in Path(self.basepath).rglob('*.card'):
			self.LoadPerson(path)
		self.VerifyRefs()
		self.MFGuess()

	# Load a new person
	#
	def LoadPerson(self, path):
		p = Person()
		p.ReadFile(path)
		p.AnalyseHeader()
		if p.uniq == None:
			print(path, ': no unique ID')
			return 1
		else:
			self.AddPerson(p.uniq, p)
			p.AnalyseEvents()
		return 0

	# Reload an individual card
	#
	def ReloadPerson(self, uniq):
		filename = self.persons[uniq].filename
		p = Person()
		p.ReadFile(filename)
		p.AnalyseHeader()
		if p.uniq == None:
			# Editing has deleted the unique ID
			print(os.path.basename(filename), ': unique ID no longer present. Correct the error and reload')
		elif p.uniq == uniq:
			# Editing has not changed the unique ID
			self.persons[uniq] = p
			p.AnalyseEvents()
		else:
			print(os.path.basename(filename), ': unique ID has changed. You should rename the file and reload')
			self.AddPerson(p.uniq, p)
			p.AnalyseEvents()

	# Guess the sex based on existing persons
	#
	def MFGuess(self):
		self.mf = {}
		for p in self.persons:
			if p == None:
				pass
			else:
				firstname = p.name.split()[0]
				try:
					if self.mf[firstname] == p.sex or self.mf[firstname] == '?':
						pass
					else:
						self.mf[firstname] = '?'
						print(firstname, 'can be male or female')
				except:
					self.mf[firstname] = p.sex

	# Return a list of all the unused entries in the database
	#
	def GetUnused(self):
		l = []
		i = 0
		for p in self.persons:
			if p == None:
				l.append(i)
			i += 1
		return l

	# Return a list of all the matching entries in the database
	# If the arg is a number, or contains a number in brackets, return the person at that index,
	# or None if out of range
	#
	def GetMatchingPersons(self, arg):
		l = []
		arg = arg.rstrip().lstrip()
		if arg.isdigit():
			idx = int(arg)
			name = None
		else:
			(name, idx) = Person.ParseCombinedNameString(arg)
		if idx != None:
			if idx < len(self.persons):
				if self.persons[idx] != None:
					l.append(self.persons[idx])
					return l
		if name == None:
			return l
		for p in self.persons:
			if p != None:
				if p.IsMatch(name):
					l.append(p)
		return l

	# Returns a list of siblings of a person, in order of data-of-birth
	#
	def GetSiblings(self, uniq):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		f_uniq = p.father_uniq
		m_uniq = p.mother_uniq

		if f_uniq == None and m_uniq == None:
			return []

		if f_uniq == None:
			f_uniq = -1			# No match with person whose father is unknown or name only
		if m_uniq == None:
			m_uniq = -1			# No match with person whose mother is unknown or name only

		sibs = []
		for pp in self.persons:
			if pp != None and (pp.father_uniq == f_uniq or pp.mother_uniq == m_uniq):
				sibs.append((pp.GetDoB(None), pp))
		sibs_in_order = sorted(sibs, key=lambda xx: xx[0])

		sibs = []
		for xx in sibs_in_order:
			sibs.append(xx[1])
		return sibs

	# Returns a list of children of a person, in order of data-of-birth
	#
	def GetChildren(self, uniq):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		children = []
		for pp in self.persons:
			if pp != None and (pp.father_uniq == uniq or pp.mother_uniq == uniq):
				children.append((pp.GetDoB(None), pp))
		children_in_order = sorted(children, key=lambda xx: xx[0])

		children = []
		for xx in children_in_order:
			children.append(xx[1])
		return children

	# Return a list of dates and partners for a person, sorted by date
	#
	def GetPartners(self, uniq):
		try:
			p = self.persons[uniq]
			return p.GetPartners()
		except:
			return None

	# Return a dictionary containing the parents, siblings and children of a person
	#
	def GetFamily(self, uniq):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		family = {}

		# The person
		family['vital'] = p.GetVitalLine()

		# Father
		pp = None
		if p.father_uniq != None:
			try:
				pp = self.persons[p.father_uniq]
				family['father_vital'] = pp.GetVitalLine()
			except:
				pp = None
		if pp == None:
			if p.father_name != None:
				family['father_vital'] = p.father_name

		# Mother
		pp = None
		if p.mother_uniq != None:
			try:
				pp = self.persons[p.mother_uniq]
				family['mother_vital'] = pp.GetVitalLine()
			except:
				pp = None
		if pp == None:
			if p.mother_name != None:
				family['mother_vital'] = p.mother_name

		siblings = []
		sibs = self.GetSiblings(p.uniq)
		for pp in sibs:
			s_vital = pp.GetVitalLine()
			if pp.uniq == p.uniq:
				s_vital = s_vital + '    (self)'
			elif pp.father_uniq == p.father_uniq and pp.mother_uniq == p.mother_uniq:
				pass
			else:
				s_vital = s_vital + '    (half)'
			siblings.append(s_vital)
		family['siblings'] = siblings

		children = []
		cc = self.GetChildren(p.uniq)
		for pp in cc:
			c_vital = pp.GetVitalLine()
			children.append(c_vital)
		family['children'] = children

		return family

	# Return an array containing a descendant tree of a person
	#
	# ToDo: insert childless partnerships
	#
	def GetDtree(self, p, level, datefmt):
		lines = []
		sp_cur = -1
		pp = p.GetPartners()
		cc = self.GetChildren(p.uniq)
		if cc == None or len(cc) == 0:
			# No children. Just person if no partners
			if pp == None or len(pp) == 0:
				line = {'level': level, 'name': p.name, 'uniq': p.uniq, 'dates': p.GetDates(datefmt),
							'vital': p.GetVitalLine(datefmt=datefmt)}
				line['spouse_name'] = ''
				line['spouse_uniq'] = ''
				line['spouse_dates'] = ''
				line['spouse_vital'] = ''
				lines.append(line)
				return lines
			# List of partnerships
			for (date, sp_uniq) in pp:
				line = {'level': level, 'name': p.name, 'uniq': p.uniq, 'dates': p.GetDates(datefmt),
							'vital': p.GetVitalLine(datefmt=datefmt)}
				try:
					sp = self.persons[sp_uniq]
					sp_vital = sp.GetVitalLine(datefmt=datefmt)
					line['spouse_name'] = sp.name
					line['spouse_uniq'] = sp.uniq
					line['spouse_dates'] = sp.GetDates(datefmt)
					line['spouse_vital'] = sp.GetVitalLine(datefmt=datefmt)
				except:
					line['spouse_name'] = '???'
					line['spouse_uniq'] = ''
					line['spouse_dates'] = ''
					line['spouse_vital'] = '???'
				lines.append(line)
			return lines

		if pp == None:
			pp = []

		# Add assumed partnerships
		for c in cc:
			to_add = True
			if p.uniq == c.father_uniq:
				sp_uniq = c.mother_uniq
				if sp_uniq == None:
					sp_uniq = c.mother_name
			else:
				sp_uniq = c.father_uniq
				if sp_uniq == None:
					sp_uniq = c.father_name
			for (d, u) in pp:
				if u == sp_uniq:
					to_add = False
					break
			if to_add:
				t = (c.GetDoB('raw'), sp_uniq)
				pp.append(t)

		# Re-sort the partnerships
		pp = sorted(pp, key=lambda xx: xx[0])

		# Now go through the partnerships and print the tree for each child
		for (d, sp_cur) in pp:
			line = {'level': level, 'name': p.name, 'uniq': p.uniq, 'dates': p.GetDates(datefmt),
						'vital': p.GetVitalLine(datefmt=datefmt)}
			if sp_cur == None:
				line['spouse_name'] = 'not known'
				line['spouse_uniq'] = ''
				line['spouse_dates'] = ''
				line['spouse_vital'] = 'not known'
			else:
				try:
					sp = self.persons[sp_cur]
					line['spouse_name'] = sp.name
					line['spouse_uniq'] = sp.uniq
					line['spouse_dates'] = sp.GetDates(datefmt)
					line['spouse_vital'] = sp.GetVitalLine(datefmt=datefmt)
				except:
					print('Partner', sp_cur, 'of', vital, 'has no unique ID')
					line['spouse_name'] = sp_cur
					line['spouse_uniq'] = ''
					line['spouse_dates'] = ''
					line['spouse_vital'] = sp_cur
					sp_vital = sp_cur
			lines.append(line)
			if level < Config.depth:
				for c in cc:
					if p.uniq == c.father_uniq:
						sp_uniq = c.mother_uniq
					else:
						sp_uniq = c.father_uniq
					if sp_uniq == sp_cur:
						lines.extend(self.GetDtree(c, level+1, datefmt))
			else:
				line = {'level': level+1, 'name': '...', 'uniq': '', 'dates': '', 'vital': '...'}
				line['spouse_name'] = ''
				line['spouse_uniq'] = ''
				line['spouse_dates'] = ''
				line['spouse_vital'] = ''
				lines.append(line)
		return lines

	# Return a descendant tree dictionary for a person.
	# The return value can be passed to a template.
	#
	def GetDescendants(self, uniq, fmt='raw'):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		desc = {}
		desc['title'] = p.GetVitalLine()
		desc['name'] = p.name
		desc['uniq'] = p.uniq
		desc['dates'] = p.GetDates(fmt)
		desc['lines'] = self.GetDtree(p, 1, fmt)
		return desc

	# Return a partial ancestor tree
	#
	def GetAtree(self, p, level):
		l = []

		if level > Config.depth:
			a = {}
			a['level'] = level+1
			a['fm'] = ''
			a['name'] = '...'
			l.append(a)
			return l
				
		if p.father_name == None and p.mother_name == None:
			return l
		if p.father_uniq == None:
			if p.father_name == None:
				a = {}
				a['level'] = level
				a['fm'] = 'F'
				a['name'] = 'not known'
				l.append(a)
			else:
				a = {}
				a['level'] = level
				a['fm'] = 'F'
				a['name'] = p.father_name
				l.append(a)
		else:
			a = {}
			a['level'] = level
			a['fm'] = 'F'
			a['name'] = self.persons[p.father_uniq].GetVitalLine()
			l.append(a)
			l.extend(self.GetAtree(self.persons[p.father_uniq], level+1))

		if p.mother_uniq == None:
			if p.mother_name == None:
				a = {}
				a['level'] = level
				a['fm'] = 'M'
				a['name'] = 'not known'
				l.append(a)
			else:
				a = {}
				a['level'] = level
				a['fm'] = 'M'
				a['name'] = p.mother_name
				l.append(a)
		else:
			a = {}
			a['level'] = level
			a['fm'] = 'M'
			a['name'] = self.persons[p.mother_uniq].GetVitalLine()
			l.append(a)
			l.extend(self.GetAtree(self.persons[p.mother_uniq], level+1))
		return l
			

	# Return an ancestor tree dictionary for a person.
	# The return value can be passed to a template.
	#
	def GetAncestors(self, uniq):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		anc = {}
		anc['title'] = p.GetVitalLine()
		anc['lines'] = self.GetAtree(p, 1)
		return anc

	# Return a TPerson object for a person of given unique id, or None if person not found
	#
	def GetTPerson(self, uniq, dateformat):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			# Out of range
			return None
		return p.GetTPerson(dateformat)

	# Return a dictionary containing the information for an individual's HTML page.
	# See templates/person-card-html.tmpl for structure and contents
	#
	def GetPersonCardInfo(self, person, dateformat = 'yearonly'):
		info = {}
		info['subj'] = person.GetTPerson(dateformat)
		info['father'] = self.GetTPerson(person.father_uniq, dateformat)
		info['mother'] = self.GetTPerson(person.mother_uniq, dateformat)

		info['notes'] = None	# ToDo

		info['siblings'] = []
		info['others'] = []
		for sib in self.GetSiblings(person.uniq):	# Non-empty: always contains the person themself
			tsib = sib.GetTPerson(dateformat)
			info['siblings'].append(tsib)
			other = None
			if tsib.uniq == person.uniq:
				# For the person thmself, remove the link and replace DoB-DoD with '(self)'
				tsib.file = None
				tsib.vital = tsib.name + ' (self)'
			elif sib.father_uniq != person.father_uniq:
				# Half-sibling; different father
				other = sib.father_uniq
			elif sib.mother_uniq != person.mother_uniq:
				# Half-sibling; different mother
				other = sib.mother_uniq
			else:
				# Full sibling: nothing to do
				pass
			if other != None:
				o_index = 0
				for o in info['others']:
					if o.uniq == other:
						tsib.other = o_index+1			# Index is 1-based
						break
					o_index += 1
				if tsib.other == None:
					tother = self.GetTPerson(other, dateformat)
					if sib.father_uniq == person.father_uniq:
						tother.other = 'Mother'
					else:
						tother.other = 'Father'
					info['others'].append(tother)
					tsib.other = len(info['others'])		# Index is 1-based
		if len(info['others']) == 0:
			# No half-siblings. Discard the empty array
			info['others'] = None
			
		info['children'] = []
		info['partners'] = []
		for ch in self.GetChildren(person.uniq):	# Might be empty
			tch = ch.GetTPerson(dateformat)
			info['children'].append(tch)
			if person.uniq == ch.father_uniq:
				tch.other = ch.mother_uniq
				other = ch.mother_name
			else:
				tch.other = ch.father_uniq
				other = ch.father_name
			if other == None:
				other = 'not known'
			if tch.other == None:
				tch.other = other					# Use name as id
				tother = T_Person(other, other)		# Use name as id
			else:
				tother = self.GetTPerson(tch.other, dateformat)
			try:
				if info['partners'][-1].uniq != tch.other:
					info['partners'].append(tother)
			except:	# When partners list is empty
				info['partners'].append(tother)
		if len(info['children']) == 0:
			# No children. Discard the empty children and partners arrays
			info['children'] = None
			info['partners'] = None

		info['events'] = None
		info['transcripts'] = None
		info['files'] = None
		return info

	# Verify that all reference links between people exist.
	# Also check that the names are correct.
	#
	def VerifyRefs(self):
		n_errs = 0
		for p in self.persons:
			if p == None:
				continue
			if p.father_uniq != None:
				n_errs += self.VerifyPerson(p.father_uniq, p.father_name, p, 'father')
			if p.mother_uniq != None:
				n_errs += self.VerifyPerson(p.mother_uniq, p.mother_name, p, 'mother')
			for ev in p.partnerships:
				(sp_name, sp_uniq) = Person.ParseCombinedNameString(ev.rest)
				e = self.VerifyPerson(sp_uniq, sp_name, p, 'spouse')
				if e == 0:
					sp = self.persons[sp_uniq]
					found = 0
					for sp_ev in sp.partnerships:
						(xx_name, xx_uniq) = Person.ParseCombinedNameString(sp_ev.rest)
						if xx_uniq == p.uniq and xx_name == p.name:
							if sp_ev.date == ev.date:
								found = 1
								break
							else:
								found = 2
					if found == 0:
						print(sp.GetVitalLine(), 'has no spouse', p.GetVitalLine())
						n_errs += 1
					elif found == 2:
						print(p.GetVitalLine(), 'has spouse', sp.GetVitalLine(),
									'with different date')
						n_errs += 1
				else:
					n_errs += e
		return n_errs

	# Verify an individual name/id against the database
	#
	def VerifyPerson(self, uniq, name, p, rel):
		msg = None
		if uniq < len(self.persons):
			pp = self.persons[uniq]
			if pp == None:
				msg = 'no person with that unique ID'
			elif pp.name != name:
				msg = 'does not match name in database ('+pp.name+')'
		else:
			msg = 'unique ID is out of range'

		if msg != None:
			print(p.GetVitalLine(), rel, name, '['+str(uniq)+'] :', msg)
			return 1
		return 0

	# Return True if a person has no recorded parents AND none of the spouses has recorded parents
	#
	def IsHead(self, p):
		if p.HasParents():
			return False
		pp = p.GetPartners()		# Returns None or a list of (date, sp_uniq) tuples
		if pp == None:
			return True
		for (x, sp_uniq) in pp:
			if sp_uniq != None and self.persons[sp_uniq].HasParents():
				return False
		return True

	# List all the patriarchs and/or matriarchs (those whose parents and parents of spouses are not recorded)
	# The argument is one of male, female, both. Default is both
	#
	def ListHeads(self, arg):
		if arg == None or len(arg) == 0:
			which = None
		else:
			argl = arg.lower()
			l = len(argl)
			if argl == 'female'[:l]:
				which = 'f'
			elif argl == 'male'[:l]:
				which = 'm'
			elif argl == 'both'[:l]:
				which = None
			else:
				print('Unrecognised parameter "' + arg + '" for heads command')
				return

		for p in self.persons:
			if p != None and self.IsHead(p):
				print(p.GetVitalLine())
		return

	# Import a GEDCOM file
	#
	def ImportGedcom(self, path):
		if len(self.persons) > 0:
			print("Merging a GEDCOM file is not supported.")
			return 1

		g = GedcomImporter(path, self)

		return 0
