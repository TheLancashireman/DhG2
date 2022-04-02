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
from DhG_Person import Person

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
		family['vital'] = p.GetVitalLine(None, None)

		# Father
		pp = None
		if p.father_uniq != None:
			try:
				pp = self.persons[p.father_uniq]
				family['father_vital'] = pp.GetVitalLine(None, None)
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
				family['mother_vital'] = pp.GetVitalLine(None, None)
			except:
				pp = None
		if pp == None:
			if p.mother_name != None:
				family['mother_vital'] = p.mother_name

		siblings = []
		sibs = self.GetSiblings(p.uniq)
		for pp in sibs:
			s_vital = pp.GetVitalLine(None, None)
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
			c_vital = pp.GetVitalLine(None, None)
			children.append(c_vital)
		family['children'] = children

		return family

	# Return an array containing a descendant tree of a person
	#
	# ToDo: insert childless partnerships
	#
	def GetDtree(self, p, level):
		vital = p.GetVitalLine(None, None)
		lines = []
		sp_cur = -1
		pp = p.GetPartners()
		cc = self.GetChildren(p.uniq)
		if cc == None or len(cc) == 0:
			# No children. Just name if no partners
			if pp == None or len(pp) == 0:
				lines.append({'level': level, 'name': vital, 'spouse': ''})
				return lines
			# List of partnerships
			for (date, sp_uniq) in pp:
				try:
					sp = self.persons[sp_uniq]
					sp_vital = sp.GetVitalLine(None, None)
					lines.append({'level': level, 'name': vital, 'spouse': sp_vital})
				except:
					lines.append({'level': level, 'name': vital, 'spouse': '???'})
			return lines

		if pp == None:
			pp = []

		# Add assumed partnerships
		for c in cc:
			to_add = True
			if p.uniq == c.father_uniq:
				sp_uniq = c.mother_uniq
			else:
				sp_uniq = c.father_uniq
			for (d, u) in pp:
				if u == sp_uniq:
					to_add = False
					break
			if to_add:
				t = (c.birth.GetDate('raw'), c.uniq)
				pp.append(t)

		# Re-sort the partnerships
		pp = sorted(pp, key=lambda xx: xx[0])

		# Now go through the partnerships and print the tree for each child
		for (d, sp_cur) in pp:
			sp_vital = self.persons[sp_cur].GetVitalLine(None, None)
			lines.append({'level': level, 'name': vital, 'spouse': sp_vital})
			for c in cc:
				if p.uniq == c.father_uniq:
					sp_uniq = c.mother_uniq
				else:
					sp_uniq = c.father_uniq
				if sp_uniq == sp_cur:
					lines.extend(self.GetDtree(c, level+1))
		return lines

	# Return a descendant tree dictionary for a person.
	# The return value can be passed to a template.
	#
	def GetDescendants(self, uniq):
		try:
			p = self.persons[uniq]
			if p == None:
				return None
		except:
			return None

		desc = {}
		desc['title'] = p.GetVitalLine(None, None)
		desc['lines'] = self.GetDtree(p, 1)
		return desc
