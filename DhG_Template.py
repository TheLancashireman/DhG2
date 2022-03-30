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

from jinja2 import Template

from DhG_Config import Config

# A class to create a file from a template
#
class DoTemplate():

	# Do everything in the constructor
	#
	#	tmpl	= template name
	#	tp		= template parameters
	#	out		= output file. None ==> stdout
	#
	def __init__(self, tmpl, tp, out):
		tmpl_name = Config.MakeTemplateName(tmpl)
		tmpl_file = open(tmpl_name, 'r')
		tmpl_text = tmpl_file.read()
		tmpl_file.close()
		template = Template(tmpl_text)
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
			outfile.close()
