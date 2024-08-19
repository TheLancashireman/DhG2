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
	config = {}

	# Initialize the class
	@staticmethod
	def Init(cfgfile):
		if cfgfile != None:
			Config.cfgfile = cfgfile

		# These values MUST be set in the config file
		Config.config['db_dir'] = None				# Location of database (must be set!)
		Config.config['tmpl_path'] = None			# Location(s) of templates. Colon-separated

		# Some default values
		Config.config['prompt'] = '(DhG) '			# Command prompt
		Config.config['editor'] = 'vi'				# Editor to use for 'edit' command
		Config.config['dateformat'] = 'raw'			# Format for dates
		Config.config['depth'] = 999999				# Max depth for trees
		Config.config['generate'] = 'public'		# Content in generated files: 'public; or 'all'
		Config.config['text-suffix'] = 'text'		# Colon-separated list of text file suffixes. No dots
		Config.config['text_path'] = None			# Locations of text transcript files. Colon-separated

		Config.ReadConfig()
		if Config.config['db_dir'] == None:
			print('Error: db_dir is not set in the config file')
			exit(1)
		if Config.config['tmpl_path'] == None:
			print('Error: tmpl_path is not set in the config file')
			exit(1)
		return

	# Get a config variable.
	# Returns None if the variable is not present in the config dictionary.
	#
	@staticmethod
	def Get(var):
		try:
			val = Config.config[var.lower()]
		except:
			val = None
		return val

	# Set a config variable.
	#
	@staticmethod
	def Set(var, val):
		Config.config[var.lower()] = val

	# Print the config
	#
	@staticmethod
	def Print():
		print('Config parameters:')
		varname = '%20s =' % 'cfgfile'
		print(varname, Config.cfgfile)

		for key in sorted(Config.config):
			varname = '%20s =' % key
			print(varname, Config.config[key])
		return

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
				if Config.SetParameter(l):
					pass
				else:
					print('Error in', Config.cfgfile, 'line', line_no, ': invalid syntax')
		f.close()
		return

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

			# Set the variable. Values that can be converted to integers are stored as such
			try:
				Config.Set(var, int(value))
			except:
				Config.Set(var, value)
		else:
			return False
		return True

	# Return the base directory (on the server) of the card files
	#
	@staticmethod
	def GetCardbase():
		if Config.Get('card_path') == None:
			if Config.Get('server_path') == None:
				cb = '/cards'
			else:
				cb = Config.Get('server_path') + '/cards'
		else:
			cb = Config.Get('card_path')
		return cb

	# Construct a file name for a card file
	#
	@staticmethod
	def MakeCardfileName(name, uniq):
		path = Config.Get('db_dir')
		b = Config.Get('branch')
		if b != None and b != '':
			path = path + '/' + b
		return Config.MakePersonfileName(name, uniq, path)

	# Construct a file name for an HTML descendants tree
	#
	@staticmethod
	def MakeHtmlDescTreeName(name, uniq):
		h = Config.Get('html_dir')
		if h == None or h == '':
			path = 'trees'
		else:
			path = h + '/trees'
		return Config.MakePersonfileName(name, uniq, path, '-descendants.html', False)

	# Construct a file name for an HTML ancestor tree
	#
	@staticmethod
	def MakeHtmlAncTreeName(name, uniq):
		h = Config.Get('html_dir')
		if h == None or h == '':
			path = 'trees'
		else:
			path = h + '/trees'
		return Config.MakePersonfileName(name, uniq, path, '-ancestors.html', False)

	# Construct a file name for an HTML person card
	#
	@staticmethod
	def MakeHtmlPersonCardName(name, uniq):
		h = Config.Get('html_dir')
		if h == None or h == '':
			path = 'cards'
		else:
			path = h + '/cards'
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
		# At the moment, only ' and . are removed (e.g. as in O'Brien, Rev. etc)
		names = re.sub('[\'.]', '', name).split()
		if surname_dir:
			prefix = prefix + names[-1] + '/'
		cardname = prefix + ''.join(names) + '-' + str(uniq) + suffix
		return cardname

	# Construct file name for an HTML surname index
	#
	@staticmethod
	def MakeHtmlSurnameIndexName():
		h = Config.Get('html_dir')
		if h == None or h == '':
			path = 'surname-index.html'
		else:
			path = h + '/surname-index.html'
		return path

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
			# No date given. Return the default if there is one, otherwise '?'
			if dflt == None:
				return '?'
			return dflt

		if fmt == None:
			# No format specified. Use the default.
			fmt = Config.Get('dateformat')

		if fmt == 'raw':
			# Raw format - return the date unmodified.
			return date

		# Convert and remove the modifier suffix
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

		# Split into YYYY, MM and DD maybe not all present.
		parts = odate.split('-')
		if len(parts) <= 1:
			# Only the year is available. Modifier applies to year
			return mod+odate

		yy = parts[0]
		if fmt == 'yearonly':
			# More than the year is available, but only the year is required. Modifier not applied.
			return yy

		mm = parts[1]
		if mm[0].upper() == 'Q':
			# Convert quarter to middle month of quarter and use 'abt.'
			qmm = [ '?', '02', '05', '08', '11' ]
			try:
				mm = qmm[int(mm[1])]
			except:
				pass
			return 'abt.'+yy+'-'+mm

		# Nothing else specified. Return "raw" date but with standardised modifier as prefix
		return mod+odate

	# Find a file called fname in a list of locations given by cfgvar.
	# If cfgvar is not given or has no value, dflt is used instead.
	# The lists are colon-separated
	#
	@staticmethod
	def FindFile(fname, cfgvar, dflt):
		locs = Config.Get(cfgvar)
		if locs == None:
			locs = dflt
		if locs == None:
			return None
		for loc in locs.split(':'):
			for root, dirs, files in os.walk(loc):
				if fname in files:
					return os.path.join(root, fname)
		return None
