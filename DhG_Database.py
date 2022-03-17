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
	def __init__(self):
		self.persons = []

	def AddPerson(self, uniq, person):
		while len(self.persons) <= uniq:
			self.persons.append(None)
		if self.persons[uniq] == None:
			self.persons[uniq] = person
		else:
			# Error: duplicate ID
			print('Error: id', uniq, 'is not unique')

	def Reload(self):
		self.persons = []
		for path in Path('/data1/family-history/database').rglob('*.card'):		# TODO: select location
			p = Person()
			try:
				p.ReadFile(path)
				p.AnalyseHeader()
				if p.uniq == None:
					print(path, ': no unique ID')
				else:
					self.AddPerson(p.uniq, p)
			except:
				print('Exception while processing ', path)

	def PrintUnused(self):
		i = 0
		for p in self.persons:
			if p == None:
				print('Unused slot', i)
			i += 1

	def PrintAllPersons(self):
		for p in self.persons:
			if p != None:
				p.PrintBriefInfo()

	def PrintMatchingPersons(self, arg):
		for p in self.persons:
			if p != None:
				p.PrintBriefIfMatch(arg)
