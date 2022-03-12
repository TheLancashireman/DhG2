#!/usr/bin/python3

# Event class - represents an event on a person's timeline

class Event:
	def __init__(self):
		self.lines = []

	def AddLine(self, line):
		self.lines.append(line)
