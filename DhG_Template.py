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
