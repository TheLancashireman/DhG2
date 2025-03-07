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
from DhG_Template import T_Indi, T_Fam, DoTemplate

# A class to export the database to a simple GEDCOM file
#
# This class is developed to export a GEDCOM file that can be imported into the LifeLines
# family tree program so that its graphical reports can be used.

class GedcomExporter():

	# Do the export in the constructor
	#
	#	ged		= gedcom file name
	#	db		= DhG database
	#
	def __init__(self, ged_name, db):
		# The DhG2 memory-resident database that we're importing into.
		self.db = db
		self.indi = []
		self.fam = []

		self.GenerateGedcomData()
		self.ExportGedcom(ged_name)
		return

	def GenerateGedcomData(self):
		# First, fill the indi array with empty records. This ensures that all unused slots are
		# defined and that the array has the correct length.
		for i in range(0, len(self.db.persons)):
			self.indi.append(None)

		# Add a dummy family that matches no-one, to ensure that the family IDs start at 1.
		t_fam = T_Fam(0, -1, -1)
		self.fam.append(t_fam)

		# Put all the persons into the indi array. At the same time, create and populate families.
		for p in self.db.persons:
			if p != None:
				# Create a T_Indi object for each person and place it in the correct location in the indi listlist.
				t_indi = T_Indi(p.uniq, self.NameToGedcom(p.name))
				self.indi[p.uniq] = t_indi

				# Set the sex if known
				if p.sex == 'm' or p.sex == 'f':
					t_indi.sex = p.sex.upper()

				# Set the birthdate
				t_indi.birthdate = p.GetDoB('gedcom')

				# Set the deathdate if the person is dead
				dod = p.GetDoD('gedcom')
				if dod != '':
					t_indi.deathdate = dod

				# Note: the following code doesn't handle parents that have a name only.
				# Find the T_Fam for this person and add this person as a child
				if p.father_uniq == None and p.mother_uniq == None:
					# Neither parent is known in the database.
					pass
				else:
					# FindTFam creates a new T_Fam if necessary, so it always returns an object
					t_fam = self.FindTFam(p.father_uniq, p.mother_uniq)
					t_fam.chil.append(p.uniq)
					t_indi.famc = t_fam.idx

				# Go through all the partnerships and add each couple to the fam list, if not
				# already there by assumed partnership.
				partners = p.GetPartners()
				if partners != None:
					for partner in partners:
						if p.sex == 'm':
							t_fam = self.FindTFam(p.uniq, partner[1])
						else:
							t_fam = self.FindTFam(partner[1], p.uniq)
						t_fam.marrdate = Config.FormatDate(partner[0], '?', 'gedcom')

		# Finally, go through the generated fam list and add the index to the husband's and wife's fams list.
		for t_fam in self.fam:
			if t_fam.husb != None and t_fam.husb >= 0:
				self.indi[t_fam.husb].fams.append(t_fam.idx)
			if t_fam.wife != None and t_fam.wife >= 0:
				self.indi[t_fam.wife].fams.append(t_fam.idx)
			
		return

	def FindTFam(self, husb, wife):
		for t_fam in self.fam:
			if t_fam.husb == husb and t_fam.wife == wife:
				return t_fam
		# Not found - create one
		t_fam = T_Fam(len(self.fam), husb, wife)
		self.fam.append(t_fam)
		return t_fam

	def ExportGedcom(self, filename):
		#self.DebugPrint()
		info = {}
		info['indi'] = self.indi
		info['fam'] = self.fam
		DoTemplate('gedcom.tmpl', info, filename, trim = True)

	def DebugPrint(self):
		# Temporary test - print the first few elements of each array
		i = 0
		for t_indi in self.indi:
			if t_indi != None:
				print(t_indi.uniq, t_indi.name, t_indi.sex, t_indi.birthdate, t_indi.deathdate, t_indi.famc, t_indi.fams)
				i += 1
				if i > 10:
					break

		i = 0
		for t_fam in self.fam:
			print(t_fam.idx, t_fam.husb, t_fam.wife, t_fam.marrdate, t_fam.chil)
			i += 1
			if i > 10:
				break
		return

	def NameToGedcom(self, name):
		parts = name.split()
		surname = parts[-1]
		gname = ' '.join(parts[0:-1]) + ' /' + surname + '/'
		return gname
