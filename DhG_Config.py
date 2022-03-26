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

# A class to hold the configuration for DhG
#
# The configuration variables can be initialised from the config file at startup
#
class Config():
	cfgfile = os.path.expanduser('~') + '/.DhG/config'		# Set on command line with -c
	prompt = '(DhG) '										# Command prompt
	db_dir = None											# Location of database (must be set!)
	branch = None											# Current family branch
	tmpl_dir = 'templates'									# Location of templates
	editor = 'vi'											# Editor to use for 'edit' command
	father = None											# Father for 'new' command
	mother = None											# Mother for 'new' command

	# In the constructor, set and read the config file
	#
	def __init__(self, cfgfile):
		if cfgfile != None:
			self.cfgfile = cfgfile
		self.ReadConfig()

	# Print the config
	#
	def Print(self):
		print('Config parameters:')
		print('cfgfile  =', self.cfgfile)
		print('prompt   =', '"'+self.prompt+'"')
		print('db_dir   =', self.db_dir)
		print('branch   =', self.branch)
		print('tmpl_dir =', self.tmpl_dir)
		print('editor   =', self.editor)
		print('father   =', self.father)
		print('mother   =', self.mother)

	# Read the config file
	#
	def ReadConfig(self):
		line_no = 0
		f = open(self.cfgfile, 'r')
		for l in f:
			line_no += 1
			l = l.rstrip().lstrip()
			if l == '' or l[0] == '#':
				pass			# Ignore comment lines and blank lines
			else:
				e = self.SetParameter(l)
				if e == 0:
					pass
				elif e == 1:
					print('Error in', self.cfgfile, 'line', line_no, ': unknown variable')
				elif e == 2:
					print('Error in', self.cfgfile, 'line', line_no, ': invalid syntax')
				else:
					print('Error in', self.cfgfile, 'line', line_no, ': to do')
		f.close()

	# Parse a parameter assignment and set an inidividual parameter
	#
	def SetParameter(self, l):
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
			if var == 'prompt':
				self.prompt = value
			elif var == 'db':
				self.db_dir = value
			elif var == 'branch':
				self.branch = value
			elif var == 'templates':
				self.tmpl_dir = value
			elif var == 'editor':
				self.editor = value
			elif var == 'father':
				self.father = value
			elif var == 'mother':
				self.mother = value
			else:
				return 1
		else:
			return 2
		return 0

	# Construct a file name for a card file
	#
	def MakeCardfileName(self, name, uniq):
		cardname = self.db_dir + '/'
		if self.branch != None and self.branch != '':
			cardname = cardname + self.branch + '/'
		names = name.split()
		cardname = cardname + names[-1] + '/' + ''.join(names) + '-' + str(uniq) + '.card'
		return cardname

	# Construct a file name for a template file
	#
	def MakeTemplateName(self, tmpl):
		if self.tmpl_dir != None and self.tmpl_dir != '':
			return self.tmpl_dir + '/' + tmpl
		return tmpl
