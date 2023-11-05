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

from jinja2 import Environment, BaseLoader
from DhG_Config import Config

# A class to load a template
#
class DhG_Loader(BaseLoader):
	# Parameter is a colon-separated list of places to look for templates
	#
	def __init__(self, path):
		self.locations = path.split(':')
		return

	# Look through the locations in order; return the first matching template
	#
	def find_first(self, template):
		for loc in self.locations:
			t = os.path.join(loc, template)
			if os.path.exists(t):
				return t
		raise TemplateNotFound(template)

	def get_source(self, environment, template):
		t = self.find_first(template)
		mtime = os.path.getmtime(t)
		with open(t) as f:
			source = f.read()
		return source, t, lambda: mtime == getmtime(path)

# A class to create a file from a template
#
class DoTemplate():

	# Do everything in the constructor
	#
	#	tmpl	= template name
	#	tp		= template parameters
	#	out		= output file. None ==> stdout
	#
	def __init__(self, tmpl_name, tp, out, trim=False):
		tp['config'] = Config
		env = Environment(trim_blocks=trim, lstrip_blocks=trim, loader=DhG_Loader(Config.Get('tmpl_path')))
		template = env.get_template(tmpl_name)
		out_text = template.render(tp = tp)
		if out == None:
			print(out_text)
		else:
			try:
				os.makedirs(os.path.dirname(out))
			except FileExistsError:
				pass
			outfile = open(out, 'w')
			outfile.write(out_text)
			outfile.write('\n')
			outfile.close()
		return

# A class to hold basic information about a person
# Used in templates
# See person-card-html.tmpl for details
#
class T_Person():
	def __init__(self, name, uniq, dob_dod = None, file = None, other = None):
		self.name = name			# Person's name
		self.uniq = uniq			# Person's id
		self.dob_dod = dob_dod		# "(DoB - DoD)" in specified form
		self.file = file			# File name (without extension) including surname directory
		self.other = other			# Index of other parent (for siblings and children)
									# Relationship to sibling (for other parent of half-siblings)
		if dob_dod == None:
			self.vital = name
		else:
			self.vital = name + ' ' + dob_dod
		return

# A class to hold a subtree of a descendants tree
# Used in templates
# See descendant-tree-html.tmpl for details
#
class T_Descendants():
	def __init__(self, level, left_person, right_person = None, children = None):
		self.level = level
		self.left = left_person
		self.right = right_person
		self.children = children

	def debug_print(self):
		if self.right == None:
			print(self.level, ':', self.left.vital)

		else:
			print(self.level, ':', self.left.vital, "===", self.right.vital)
		if self.children == None:
			print('No children')
		else:
			for x in self.children:
				x.debug_print()
		return

# A class to hold a row of the event timeline
# Used in templates
# See descendant-tree-html.tmpl for details
#
class T_Event():
	def __init__(self, date, etype, tperson):
		self.date = date		# Formatted date of the event
		self.evtype = etype		# Event type
		self.tperson = tperson	# T_Person object for partner in marriage etc.
		self.information = []	# Array of T_EvInfo objects containing information about or extracted from the event
		self.sources = []		# Array of T_Source objects
		return

# A class to hold an item of information about an event
#
class T_EvInfo():
	def __init__(self, caption, info):
		self.caption = caption		# Type of information (Place, Abode etc.)
		self.info = info			# The information (text)
		self.url = None				# Link to a supporting page
		self.moreinfo = None		# List of supplementary information (T_EvInfo objects with no moreinfo)
		return

	# Add more text to the info
	#
	def AppendLine(self, text):
		if self.info != '':
			self.info += '\n'
		self.info += text
		return

	# Add more info to the array. Create the array if None
	#
	def AddInfo(self, info):
		if self.moreinfo == None:
			self.moreinfo = [info]
		else:
			self.moreinfo.append(info)
		return

# A class to hold a source reference
#
class T_Ref():
	def __init__(self, text, link):
		self.text = text
		self.link = link
		return

# A class to hold a source of information
#
class T_Source():
	def __init__(self, descr):
		self.descr = descr			# Description of the source
		self.refs = None			# Array of links. Each is a T_Ref object
									# URL can be local (#Tn, #Fn) or global (http/https/etc.)
		self.moreinfo = None		# List of supplementary information (T_EvInfo objects with no moreinfo)
		return

	# Add a reference to the array. Create the array if None
	#
	def AddRef(self, text, link):
		ref = T_Ref(text, link)
		if self.refs == None:
			self.refs = [ref]
		else:
			self.refs.append(ref)
		return

	# Add more info to the array. Create the array if None
	#
	def AddInfo(self, info):
		if self.moreinfo == None:
			self.moreinfo = [info]
		else:
			self.moreinfo.append(info)
		return

# A class to hold a transcript
#
class T_Transcript():
	def __init__(self, ref, text):
		self.ref = ref				# Reference (Tn). Used in column 1 and as anchor.
		self.text = text			# The transcript. Will be shown in <pre> environment.
		return

	def AppendLine(self, text):
		if self.text != '':
			self.text += '\n'
		self.text += text
		return

# A class to hold a file
#
class T_File():
	def __init__(self, ref, ftype, name):
		self.ref = ref			# Reference (Fn). Used in column 1 and as anchor.
		self.tref = None		# Reference (Tm) to content of this file in a T_Transcript object
		self.ftype = ftype		# File type (transcript, image etc)
		self.name = name		# File name
		return

# A class to hold a node in the ancestor tree
#
class T_AncestorNode():
	def __init__(self, level, subj):
		self.level = level		# The level. Level 1 is the top level
		self.subj = subj		# A T_Person object representing the person at this level
		self.parents = None		# An array of two elements that can be None or a T_AncestorNode() object

	# Get a parent from the parents array.
	# The index must be 0 or 1
	#
	def GetParent(self, index):
		if self.parents == None:
			return None
		return self.parents[index]

	# Add a parent to the parents array. Create the array if necessary
	# The index must be 0 or 1
	#
	def AddParent(self, index, anode):
		if self.parents == None:
			self.parents = [None, None]
		self.parents[index] = anode
		return
