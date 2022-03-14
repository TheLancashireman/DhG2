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
