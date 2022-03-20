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



# Event class - represents an event on a person's timeline
#
class Event:
	def __init__(self):
		self.lines = []
		self.ower = None
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
		parts = self.lines[0].split()
		try:
			self.date = parts[0]
			self.etype = parts[1]
		except:
			print('Insufficient fields in event date line', self.lines[0], 'in', owner.filename)

		if len(self.lines) > 2:
			rest = ' '.join(self.lines[2:])
