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

from jinja2 import Template

from DhG_Database import Database
from DhG_Person import Person
from DhG_Config import Config
from DhG_Template import DoTemplate
from DhG_Shell import DhG_Shell

# A class to extend the DhG command interpreter with some special commands. To use this feature,
# run this Python program in the same way as you would run the standard DhG_Shell.py program.
#
# These commands probably won't be very useful unless your database content is very similar to the
# author's database.
#
# z_image_no_transcript() prints a list of +Source objects within the events, that have a -File Image
#  sub-object but neither a -Transcript sub-object nor a -File Transcript sub-object with a suffix that
#  matches the config list for text files. If the 'strict' argument is give, a file transcript is required.
#
#  The command differentiates between England and Wales census records and all other records by means
#  of the 'census' argument. England and Wales census records have the form +Source Census record along
#  with either an RG or an HO107 record ident.
#
class DhG_Specials(DhG_Shell):
	# In the constructor, read the command line
	#
	def __init__(self):
		super().__init__()
		return

	def do_z_image_no_transcript(self, arg):
		'''
z_image_no_transcript is a special command to find all events for which there is a source with an image
but no transcript.

The arguments can be a mixture of:

* census - look at England and Wales census events only. If absent, all other events are considered.
* strict - only consider file transcripts; ignore inline transcripts

Anything else is ignored

The output shows the person and the source. Thus a person may result in multiple lines of output.
		'''
		strict = False
		ew_census = False
		args = arg.lower().split()
		for a in args:
			if a == 'strict':
				strict = True
			elif a == 'census':
				ew_census = True
		l = self.db.GetMatchingPersons('')
		for p in l:
			for e in p.events:
				source = None
				has_image = False
				has_transcript = False
				for line in e.lines:
					if len(line) < 1:
						pass
					elif line[0] == '+':
						if source != None and has_image and not has_transcript:
							print(p.GetVitalLine(), e.date, e.etype, source)
						source = None
						has_image = False
						has_transcript = False
						fields = line.split(maxsplit=4)
						if ( len(fields) >= 4 and
						     fields[0].lower() == '+source' and
						     fields[1].lower() == 'census' and
						     fields[2].lower() == 'record' and
							 ( fields[3][0:2] == 'RG' or fields[3][0:5] == 'HO107' ) ):
							if ew_census:
								source = line
						elif (len(fields) >= 1 and
						      fields[0].lower() == '+source'):
							if not ew_census:
								source = line
						else:
							source = None
					elif line[0] == '-':
						fields = line.split(maxsplit=4)
						if len(fields) > 2 and fields[0].lower() == '-file':
							if fields[1].lower() == 'image':
								has_image = True
							elif fields[1].lower() == 'transcript':
								(base, ext) = os.path.splitext(fields[2])
								if ext == '' or ext[0] != '.':
									pass
								elif ext[1:] in Config.Get('text-suffix').split(':'):
									has_transcript = True
						elif fields[0].lower() == '-transcript':
							if not strict:
								has_transcript = True
				if source != None and has_image and not has_transcript:
					print(p.GetVitalLine(), e.date, e.etype, source)
		return

if __name__ == '__main__':
	while True:
		DhG_Specials().cmdloop()
