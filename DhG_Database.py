#!/usr/bin/python3
#
# A class to represent the entire database
#
# The persons in the database are stored in an array indexed by the unique ID
# The order in which the elements arrice is not known, so the gaps in the array are filled
# with None as the loading proceeeds.

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
