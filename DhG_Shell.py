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
import traceback
import getopt

from DhG_Database import Database
from DhG_Person import Person

# A class to implement a command interpreter for the interactive DhG
#
class DhG_Shell(cmd.Cmd):
	# Message that is displayed in response to -v/--version
	version = 'This is DhG version 2\n\n'+\
		'(c) David Haworth (dave@fen-net.de; http://thelancashireman.org)\n'+\
		'DhG comes with ABSOLUTELY NO WARRANTY. It is free free software, and you are welcome\n'+\
		'to redistribute it under certain conditions; please read the accompanying file\n'+\
		'gpl-3.0.txt for details.\n'

	# Message that is displayed in response to -h/--help and when the command line is incorrect
	usage = 'Usage: ' + sys.argv[0] + ' [options] [script-file ...]\n'+\
		'  Valid options:\n'+\
		'    -h --help                     print some help text and exit\n'+\
		'    -v --version                  print the version and exit\n'+\
		'    -c cfgfile  --config=cfgfile  use cfgfile as the configuration file. Default ~/.DhG/config\n'+\
		'  If more than one cfgfile is specified, the last one is used.\n'+\
		'  Each argument is treated as a script file.\n'+\
		'  The commands in the scripts are executed after loading the database.\n'+\
		'  After executing the scripts, ' + sys.argv[0] + ' drops into interactive mode.\n'+\
		'  A quit command in one of the scripts terminates the program immediately.'

	# Message that is displayed on startup
	intro = version + '\nType help or ? to list commands.'

	prompt = '(DhG) '
	cfgfile = os.path.expanduser('~') + '/.DhG/config'
	scripts = []
	db_dir = None
	branch = None
	db = None

	# In the constructor, read the command line
	#
	def __init__(self):
		dropout = False
		super().__init__()
		try:
			(opts, args) = getopt.gnu_getopt(sys.argv[1:], "hvc:", ["help", "version", "config="])
		except getopt.GetoptError as err:
			# print help information and exit:
			print(err)  # will print something like "option -a not recognized"
			self.Usage()
			exit(1)
		for (opt, optarg) in opts:
			if opt == '-h' or opt == '--help':
				self.Usage()
				dropout = True
			if opt == '-v' or opt == '--version':
				self.Version()
				dropout = True
			if opt == '-c' or opt == '--config':
				self.cfgfile = optarg
		self.scripts = args
		if dropout:
			exit(0)
		self.ReadConfig()

	def Usage(self):
		print(self.usage)

	def Version(self):
		print(self.version)

	def ReadConfig(self):
		line_no = 0
		f = open(self.cfgfile, 'r')
		for l in f:
			line_no += 1
			l = l.rstrip().lstrip()
			if l == '' or l[0] == '#':
				pass			# Ignore comment lines and blank lines
			else:
				# Split on the '=' sign. There should be exactly one
				parts = l.split('=')
				if len(parts) == 2:
					# Remove leading and trailing whitespace
					var = parts[0].rstrip().lstrip().lower()
					value = parts[1].rstrip().lstrip()

					# Remove quotes from the value, if they match
					if value[0] == '"' and value[-1] == '"':
						value = value[1:-1]
					elif value[0] == "'" and value[-1] == "'":
						value = value[1:-1]

					# Set the variable
					if var == 'db':
						self.db_dir = value
					elif var == 'branch':
						self.branch = value
					elif var == 'prompt':
						self.prompt = value
					else:
						print('Error in', self.cfgfile, 'line', line_no, ': unknown variable')
				else:
					print('Error in', self.cfgfile, 'line', line_no, ': invalid syntax')
		f.close()

	# Before the command loop, create and load the database
	#
	def preloop(self):
		self.db = Database(self.db_dir)
		self.db.Reload()

	def onecmd(self, str):
		try:
			super().onecmd(str)
		except Exception:
			print(traceback.format_exc())

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
				if name[3:] == keyword:
					return line				# Exact match
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

	# Report that list of matches is ambiguous
	#
	def PrintPersonList(self, l, arg):
		if len(l) < 1:
			print('No entry', arg, 'found in the database')
		else:
			for p in l:
				print(p.GetVitalLine(0, 0))		# ToDo: parameters

	# Edit a card using the specified editor
	#
	def EditCard(self, editor, arg):
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			os.system(editor + ' ' + str(l[0].filename))
		else:
			self.PrintPersonList(l, arg)

	# Report the ambiguous command error
	#
	def do_ambiguous_command_error(self, arg):
		print('Ambiguous command. Possible matches are: ', arg)

	# All the "real" commands:
	#
	def do_quit(self, arg):
		'Quit the program'
		exit(0)

	def do_reload(self, arg):
		'Reload the database'
		self.db.Reload()

	def do_unused(self, arg):
		'List all the unused IDs in the database'
		l = self.db.GetUnused()
		for i in l:
			print('['+str(i)+']')

	def do_list(self, arg):
		'List all the persons in the database'
		self.do_find('')

	def do_find(self, arg):
		'Print a list of persons that match the given terms'
		l = self.db.GetMatchingPersons(arg)
		for p in l:
			print(p.GetVitalLine(0, 0))		# ToDo: parameters

	def do_search(self, arg):
		'Print a list of persons that match the given terms'
		do_find(arg)

	def do_tl(self, arg):
		'Print the timeline for a person'
		self.do_timeline(arg)

	def do_timeline(self, arg):
		'Print the timeline for a person'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			tl = l[0].GetTimeline()
			for txt in tl:
				print(txt)
		else:
			self.PrintPersonList(l, arg)

	def do_vi(self, arg):
		'Edit a person\'s card using vi'
		self.EditCard('vi', arg)

	def do_vim(self, arg):
		'Edit a person\'s card using vim'
		self.EditCard('vim', arg)

	def do_edit(self, arg):
		'Edit a card using $VISUAL'
		self.EditCard('vi', arg)			# ToDo: environment variable or config

	def do_new(self, arg):
		'Create a new person in the database'
		print('do_new(): ', arg)
	
	def do_family(self, arg):
		'Show a person\'s immediate family'
		print('do_family(): ', arg)

	def do_descendants(self, arg):
		'Print a descendants tree for a given person'
		print('do_descendants(): ', arg)

	def do_ancestors(self, arg):
		'Print an ancestors tree for a given person'
		print('do_ancestors(): ', arg)

	def do_test(self, arg):
		'For testing code snippets. ToDo: delete'
		print('do_test(): ', arg)
		(name, uniq) = Person.ParseCombinedNameString(arg)
		print(name, uniq);
	

if __name__ == '__main__':
	while True:
		DhG_Shell().cmdloop()
