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
import cmd
import re

from DhG_Database import Database

# A class to implement a command interpreter for the interactive DhG
#
class DhG_Shell(cmd.Cmd):
	intro = 'This is DhG\n\n'+\
		'(c) David Haworth (dave@fen-net.de; http://thelancashireman.org)\n'+\
		'DhG comes with ABSOLUTELY NO WARRANTY. It is free free software, and you are welcome\n'+\
		'to redistribute it under certain conditions; please read the accompanying file\n'+\
		'gpl-3.0.txt for details.\n\n'+\
		'Type help or ? to list commands.'
	prompt = '(DhG) '
	file = None
	db = None

	def preloop(self):
		self.db = Database()
		self.db.Reload()

	# Ignore blank commands
	#
	def emptyline(self):
		return

	# Preprocess the command: try to find a match for an abbreviated command.
	# If there's more than one match, prepend the ambiguous_command_error command to the line
	# and let the do_ambiguous_command_error() handler report the error. This means that,
	# if necessary, the emptyline() function can do something useful.
	#
	def precmd(self, line):
		line = line.rstrip().lstrip()
#		print('precmd():', line)
		if line == '':
			return line
		match = re.search(r'[ 0-9]', line)
		if match:
			keyword = line[0:match.start()]
#			print('Digit/space found at', match.start(), 'keyword:', keyword)
		else:
			keyword = line
		keylen = len(keyword)
		cmdmatch = []
		for name in self.get_names():
			if name != 'do_ambiguous_command_error' and name[0:3] == 'do_' and name[3:keylen+3] == keyword:
#				print('Possible match:', name[3:])
				cmdmatch.append(name[3:])
		if len(cmdmatch) == 1:
			line = cmdmatch[0] + line[keylen:]
#			print('Completed command:', line)
		elif len(cmdmatch) > 1:
#			print('Ambiguous command: \''+keyword+'\'')
			line = 'ambiguous_command_error'
			for m in cmdmatch:
				line = line + ' ' + m
		return line

	# Report the ambiguous command error
	#
	def do_ambiguous_command_error(self, arg):
		print('Ambiguous command. Possible matches are: ', arg)

	# All the "real" commands:
	#
	def do_quit(self, arg):
		'Quit the program'
		exit(0)

	def do_unused(self, arg):
		'List all the unused IDs in the database'
		self.db.PrintUnused()

	def do_list(self, arg):
		'List all the persons in the database'
		self.db.PrintAllPersons()

	def do_find(self, arg):
		'Print a list of persons that match the given terms'
		self.db.PrintMatchingPersons(arg)

	def do_family(self, arg):
		'Show a person\'s immediate family'
		print('do_family(): ', arg)

	def do_descendants(self, arg):
		'Print a descendants tree for a given person'
		print('do_descendants(): ', arg)

	def do_ancestors(self, arg):
		'Print an ancestors tree for a given person'
		print('do_ancestors(): ', arg)

	def do_search(self, arg):
		'Print a list of persons that match the given terms'
		print('do_search(): ', arg)

	def do_edit(self, arg):
		'Edit a person\'s card using $EDITOR'
		print('do_edit(): ', arg)

	def do_vi(self, arg):
		'Edit a person\'s card using vi'
		print('do_vi(): ', arg)

	def do_new(self, arg):
		'Create a new person in the database'
		print('do_new(): ', arg)
	

if __name__ == '__main__':
	DhG_Shell().cmdloop()
