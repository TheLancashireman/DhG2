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
import re

# A class to hold the configuration for DhG
#
# The class only contains static variables and methods.
# The configuration variables can be initialised from the config file at startup
#

class Config():
	cfgfile = os.path.expanduser('~') + '/.DhG/config'		# Set on command line with -c
	prompt = '(DhG) '										# Command prompt
	db_dir = None											# Location of database (must be set!)
	branch = None											# Current family branch
	tmpl_dir = 'templates'									# Location of templates
	html_dir = None											# Where to put the HTML output
	server_path = None										# Path to htmldir on server (for links)
	editor = 'vi'											# Editor to use for 'edit' command
	dateformat = 'raw'										# Format for dates
	depth = 999999											# Max depth for trees
	father = None											# Father for 'new' command
	mother = None											# Mother for 'new' command

	# Initialize the class
	@staticmethod
	def Init(cfgfile):
		if cfgfile != None:
			Config.cfgfile = cfgfile
		Config.ReadConfig()

	# Print the config
	#
	@staticmethod
	def Print():
		print('Config parameters:')
		print('cfgfile     =', Config.cfgfile)
		print('prompt      =', '"'+Config.prompt+'"')
		print('db_dir      =', Config.db_dir)
		print('branch      =', Config.branch)
		print('tmpl_dir    =', Config.tmpl_dir)
		print('html_dir    =', Config.html_dir)
		print('editor      =', Config.editor)
		print('dateformat  =', Config.dateformat)
		print('depth       =', Config.depth)
		print('father      =', Config.father)
		print('mother      =', Config.mother)

	# Read the config file
	#
	@staticmethod
	def ReadConfig():
		line_no = 0
		f = open(Config.cfgfile, 'r')
		for l in f:
			line_no += 1
			l = l.rstrip().lstrip()
			if l == '' or l[0] == '#':
				pass			# Ignore comment lines and blank lines
			else:
				e = Config.SetParameter(l)
				if e == 0:
					pass
				elif e == 1:
					print('Error in', Config.cfgfile, 'line', line_no, ': unknown variable')
				elif e == 2:
					print('Error in', Config.cfgfile, 'line', line_no, ': invalid syntax')
				else:
					print('Error in', Config.cfgfile, 'line', line_no, ': to do')
		f.close()

	# Parse a parameter assignment and set an inidividual parameter
	#
	@staticmethod
	def SetParameter(l):
		# Split on the '=' sign. There should be exactly one
		parts = l.split('=')
		if len(parts) == 2:
			# Remove leading and trailing whitespace
			var = parts[0].rstrip().lstrip().lower()
			value = parts[1].rstrip().lstrip()

			# Remove quotes from the value, if they match

			try:
				if value[0] == '"' and value[-1] == '"':
					value = value[1:-1]
				elif value[0] == "'" and value[-1] == "'":
					value = value[1:-1]
			except:
				pass

			# Set the variable
			if var == 'prompt':
				Config.prompt = value
			elif var == 'db':
				Config.db_dir = value
			elif var == 'branch':
				Config.branch = value
			elif var == 'templates':
				Config.tmpl_dir = value
			elif var == 'htmldir':
				Config.html_dir = value
			elif var == 'serverpath':
				Config.server_path = value
			elif var == 'editor':
				Config.editor = value
			elif var == 'dateformat':
				Config.dateformat = value
			elif var == 'depth':
				try:
					Config.depth = int(value)
				except:
					print('The value of "depth" must be an integer')
			elif var == 'father':
				Config.father = value
			elif var == 'mother':
				Config.mother = value
			else:
				return 1
		else:
			return 2
		return 0

	# Construct a file name for a card file
	#
	@staticmethod
	def MakeCardfileName(name, uniq):
		path = Config.db_dir
		if Config.branch != None and Config.branch != '':
			path = path + '/' + Config.branch
		return Config.MakePersonfileName(name, uniq, path)

	# Construct a file name for an HTML descendants tree
	#
	@staticmethod
	def MakeHtmlDescTreeName(name, uniq):
		if Config.html_dir == None or Config.html_dir == '':
			path = 'trees'
		else:
			path = Config.html_dir + '/trees'
		return Config.MakePersonfileName(name, uniq, path, '-descendants.html', False)

	# Construct a file name for an HTML person card
	#
	@staticmethod
	def MakeHtmlPersonCardName(name, uniq):
		if Config.html_dir == None or Config.html_dir == '':
			path = 'cards'
		else:
			path = Config.html_dir + '/cards'
		return Config.MakePersonfileName(name, uniq, path, '.html', True)

	# Construct a file name for a person's file
	#
	@staticmethod
	def MakePersonfileName(name, uniq, prefix, suffix='.card', surname_dir=True):
		if prefix == None:
			prefix = ''
		elif prefix != '':
			prefix = prefix + '/'
		# Remove unwanted characters from name and split on spaces
		# At the moment, only ' is removed (e.g. as in O'Brien)
		names = re.sub('[\']', '', name).split()
		if surname_dir:
			prefix = prefix + names[-1] + '/'
		cardname = prefix + ''.join(names) + '-' + str(uniq) + suffix
		return cardname

	# Construct a file name for a template file
	#
	@staticmethod
	def MakeTemplateName(tmpl):
		if Config.tmpl_dir != None and Config.tmpl_dir != '':
			return Config.tmpl_dir + '/' + tmpl
		return tmpl

	# Returns a "normalised" version of a given date according to the specified format
	#
	# Date formats are:
	#	raw      -- exactly as entered
	#	cooked	 -- approximations rendered as abt, bef and aft, quarters changed to abt <middle month>
	#	yearonly -- only the year, approxmations ignored if they come after month or day.
	# Any format not lists above is treated as cooked.
	#
	@staticmethod
	def FormatDate(date, dflt, fmt):
		if date == None:
			if dflt == None:
				return '?'
			return dflt
		if fmt == None:
			fmt = Config.dateformat
		if fmt == 'raw':
			return date

		odate = date
		mod = odate[-1]
		if mod == '~':
			mod = 'abt.'
		elif mod == '<':
			mod = 'bef.'
		elif mod == '>':
			mod = 'aft.'
		else:
			mod = ''
		if mod != '':
			odate = odate[0:-1]

		parts = odate.split('-')
		if len(parts) <= 1:
			# Only the year is available. Modifier applies to year
			return mod+odate

		yy = parts[0]
		if fmt == 'yearonly':
			# More than the year is available, but only the year is required.
			return mod+yy

		mm = parts[1]
		if mm[0].upper() == 'Q':
			# Convert quarter to middle month of quarter and use 'abt.'
			qmm = [ '?', '02', '05', '08', '11' ]
			try:
				mm = qmm[int(mm[1])]
			except:
				pass
			return 'abt.'+yy+'-'+mm

		# Nothing else specified. Return "raw" date but with standardise modifier as prefix
		return mod+odate
