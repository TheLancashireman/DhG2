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

# A class to implement a command interpreter for the interactive DhG
#
class DhG_Shell(cmd.Cmd):
	# Message that is displayed in response to -v/--version
	version = 'This is DhG version 2\n\n'+\
		'(c) David Haworth (https://thelancashireman.org)\n'+\
		'DhG comes with ABSOLUTELY NO WARRANTY. It is free software, and you are welcome\n'+\
		'to redistribute it under certain conditions; please read the accompanying file\n'+\
		'gpl-3.0.txt for details.\n'

	# Message that is displayed in response to -h/--help and when the command line is incorrect
	usage = 'Usage: ' + sys.argv[0] + ' [options] [script-file ...]\n'+\
		'  Valid options:\n'+\
		'    -h --help                     print some help text and exit\n'+\
		'    -v --version                  print the version and exit\n'+\
		'    -c cfgfile  --config=cfgfile  use cfgfile as the configuration file. Default ~/.DhG/config\n'+\
		'  If more than one cfgfile is specified, the last one is used.\n'+\
		'  The script-file arguments are currently ignored.'
#		'  Each argument is treated as a script file.\n'+\
#		'  The commands in the scripts are executed after loading the database.\n'+\
#		'  After executing the scripts, ' + sys.argv[0] + ' drops into interactive mode.\n'+\
#		'  A quit command in one of the scripts terminates the program immediately.'

	# Message that is displayed on startup
	intro = '\nType help or ? to list commands.'

	# List of scripts, taken from the command line
	scripts = []

	# The database
	db = None

	# Configuration variables can be set in the config file
	prompt = '(DhG) '	# Parent class needs a copy

	# In the constructor, read the command line
	#
	def __init__(self):
		dropout = False
		cfgfile = None
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
				cfgfile = optarg
		self.scripts = args
		if dropout:
			exit(0)
		Config.Init(cfgfile)
		self.prompt = Config.Get('prompt')
		return

	def Usage(self):
		print(self.usage)
		return

	def Version(self):
		print(self.version)
		return

	# Before the command loop, create and load the database
	#
	def preloop(self):
		self.db = Database(Config.Get('db_dir'))
		self.db.Reload()

	def onecmd(self, str):
		try:
			super().onecmd(str)
		except Exception:
			print(traceback.format_exc())
		return

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
		if line[0] == '!':
			return 'shell ' + line[1:]
		match = re.search(r'[ 0-9\[]', line)
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
			line = cmdmatch[0] + ' ' + line[keylen:]
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
				print(p.GetVitalLine())		# ToDo: parameters
		return

	# Edit a card using the specified editor
	#
	def EditCard(self, editor, arg):
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			print('Editing', os.path.basename(l[0].filename))
			os.system(editor + ' ' + str(l[0].filename))
			self.db.ReloadPerson(l[0].uniq)
		else:
			self.PrintPersonList(l, arg)
		return

	# Report the ambiguous command error
	#
	def do_ambiguous_command_error(self, arg):
		print('Ambiguous command. Possible matches are: ', arg)
		return

	# All the "real" commands:
	#
	def do_quit(self, arg):
		'Quit the program'
		exit(0)

	def do_set(self, arg):
		'Set a config parameter'
		if arg == '':
			Config.Print()
			return
		if not Config.SetParameter(arg):
			print('Error : invalid syntax for set')
		return

	def do_reload(self, arg):
		'Reload the database'
		self.db.Reload()
		return

	def do_unused(self, arg):
		'List all the unused IDs in the database'
		l = self.db.GetUnused()
		for i in l:
			print('['+str(i)+']')
		return

	def do_list(self, arg):
		'List all the persons in the database'
		self.do_find('')
		return

	def do_find(self, arg):
		'Print a list of persons that match the given terms'
		l = self.db.GetMatchingPersons(arg)
		for p in l:
			print(p.GetVitalLine())		# ToDo: parameters
		return

	def do_search(self, arg):
		'Print a list of persons that match the given terms'
		self.do_find(arg)
		return

	def do_tl(self, arg):
		'Print the timeline for a person'
		self.do_timeline(arg)
		return

	def do_timeline(self, arg):
		'Print the timeline for a person'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			tl = l[0].GetTimeline()
			for txt in tl:
				print(txt)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_vi(self, arg):
		'Edit a person\'s card using vi'
		self.EditCard('vi', arg)
		return

	def do_vim(self, arg):
		'Edit a person\'s card using vim'
		self.EditCard('vim', arg)
		return

	def do_edit(self, arg):
		'Edit a card using config.editor'
		self.EditCard(Config.Get('editor'), arg)
		return

	def do_new(self, arg):					# ToDo: refactor this function
		'Create a new person in the database'
		(name, uniq) = Person.ParseCombinedNameString(arg)
		#db.CreateNewPerson(name, uniq)
		if name == '':
			print('Use "new forename(s) surname" to add a new person')
			return
		if uniq == None:
			uniq = len(self.db.persons)
			if uniq < 1:
				uniq = 1
		else:
			if uniq < 1:
				print('Unique id must be a positive number')
				return
			if uniq < len(self.db.persons) and self.db.persons[uniq] != None:
				print('Unique id', uniq, 'is already in use')
				return
		cardname = Config.MakeCardfileName(name, uniq)
		try:
			names = name.split()
			firstname = names[0]
			s = self.db.mf[firstname]
		except:
			s = '?'
		tp = {
			'name': name,
			'uniq': uniq,
			'sex': s,
			'father': Config.Get('father'),
			'mother': Config.Get('mother')
			}
		DoTemplate('new-person-card.tmpl', tp, cardname)
		if self.db.LoadPerson(cardname) == 0:
			print('Created new person ', name, '['+str(uniq)+']')
		return

	def do_family(self, arg):
		'Show a person\'s immediate family'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			fam = self.db.GetFamily(l[0].uniq)
			DoTemplate('family-text.tmpl', fam, None)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_descendants(self, arg):
		'Print a descendants tree for a given person'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			save = Config.Get('generate')
			Config.Set('generate', 'all')
			try:
				desc = self.db.GetDescendants(l[0].uniq, 'yearonly')
				DoTemplate('descendant-tree-text.tmpl', desc, None, trim = True)
			except Exception:
				print(traceback.format_exc())
			Config.Set('generate', save)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_ancestors(self, arg):
		'Print an ancestors tree for a given person'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			anc = self.db.GetAncestorsObsolete(l[0].uniq)
			DoTemplate('ancestor-tree-text.tmpl', anc, None)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_heads(self, arg):
		'List all the patriarchs and/or matriarchs (those whose parents and parents of spouses are not recorded).\nThe argument is one of male, female, both. Default is both'
		self.db.ListHeads(arg)
		return

	def do_verify(self, arg):
		'Verify all the person references in the database'
		if self.db.VerifyRefs() == 0:
			print('Verification complete; no errors')
		return

	def do_gedi(self, arg):
		'Import a GEDCOM file'
		self.db.ImportGedcom(arg)
		return

	def do_shell(self, arg):
		'Run a command in a shell'
		os.system(arg)
		return

	def do_htmldescendants(self, arg):
		'Create a descendants tree in HTML for a given person'
		if len(arg) > 0 and arg[0] == '@':
			f = open(arg[1:], 'r')
			erase = '          '
			lastlen = 0
			for line in f:
				line = line.rstrip().lstrip()
				id = line.split(' ')[0]
				if id == '' or id[0] == '#':
					pass			# Ignore comment lines and blank lines
				else:
					l = self.db.GetMatchingPersons(id)
					if len(l) == 1:
						person = l[0]
						print('HTML descendants for', person.GetVitalLine())
						file = Config.MakeHtmlDescTreeName(person.name, person.uniq)
						desc = self.db.GetDescendants(person.uniq, 'yearonly')
						DoTemplate('descendant-tree-html.tmpl', desc, file, trim = True)
					else:
						print('Invalid or ambiguous line "'+line+'" found in', arg[1:])
			f.close()
			return
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			person = l[0]
			file = Config.MakeHtmlDescTreeName(person.name, person.uniq)
			desc = self.db.GetDescendants(person.uniq, 'yearonly')
			DoTemplate('descendant-tree-html.tmpl', desc, file, trim = True)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_hd(self, arg):	# Abbreviated command
		'Create a descendants tree in HTML for a given person. Abbreviation of htmldescendants'
		self.do_htmldescendants(arg)
		return

	def do_htmlancestors(self, arg):
		'Create an ancestor tree (Ahnentafel) in HTML for a given person'
		if len(arg) > 0 and arg[0] == '@':
			f = open(arg[1:], 'r')
			erase = '          '
			lastlen = 0
			for line in f:
				line = line.rstrip().lstrip()
				id = line.split(' ')[0]
				if id == '' or id[0] == '#':
					pass			# Ignore comment lines and blank lines
				else:
					l = self.db.GetMatchingPersons(id)
					if len(l) == 1:
						person = l[0]
						print('HTML ancestors for', person.GetVitalLine())
						file = Config.MakeHtmlAncTreeName(person.name, person.uniq)
						anc = self.db.GetAncestors(person.uniq, 'yearonly')
						DoTemplate('ancestor-tree-html.tmpl', anc, file, trim = True)
					else:
						print('Invalid or ambiguous line "'+line+'" found in', arg[1:])
			f.close()
			return
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			person = l[0]
			file = Config.MakeHtmlAncTreeName(person.name, person.uniq)
			anc = self.db.GetAncestors(person.uniq, 'yearonly')
			DoTemplate('ancestor-tree-html.tmpl', anc, file, trim = True)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_ha(self, arg):	# Abbreviated command
		'Create an ancestor tree (Ahnentafel) in HTML for a given person. Abbreviation of htmlancestors'
		self.do_htmlancestors(arg)
		return

	def do_htmlcard(self, arg):
		'Create a cardfile in HTML for a given person'
		if len(arg) > 0 and arg[0] == '@':
			listfile = arg[1:]
			# Special cases of listfile
			if listfile == 'all' or listfile == 'public':
				erase = '          '
				lastlen = 0
				for person in filter(lambda x: x != None, self.db.persons):
					if listfile == 'all' or self.db.IsPublic(person.uniq):
						# Erase the previous line
#						if lastlen > 0:
#							while len(erase) < lastlen:
#								erase += '     '
#							print('HTML card for', erase[0:lastlen], end='\r')
#						print('HTML card for', person.GetVitalLine(), end='\r')
#						lastlen = len(person.GetVitalLine())
						print('HTML card for', person.GetVitalLine())
						try:
							file = Config.MakeHtmlPersonCardName(person.name, person.uniq)
							info = self.db.GetPersonCardInfo(person, 'yearonly')
							DoTemplate('person-card-html.tmpl', info, file, trim = True)
						except Exception:
							print()
							print(traceback.format_exc())
				print()
			else:
				print('Printing cards of list of persons is not supported yet')
			return
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			person = l[0]
			file = Config.MakeHtmlPersonCardName(person.name, person.uniq)
			info = self.db.GetPersonCardInfo(person, 'yearonly')
			DoTemplate('person-card-html.tmpl', info, file, trim = True)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_hc(self, arg):
		'Create a cardfile in HTML for a given person. Abbreviation of htmlcard'
		self.do_htmlcard(arg)
		return

	def do_htmlindex(self, arg):
		'Create a surname index in HTML'
		private = False
		if len(arg) > 0:
			if arg == '@all':
				private = True
			elif arg == '@public':
				private = False
			else:
				print('Argument must be either @public or @all')
				return
		file = Config.MakeHtmlSurnameIndexName()
		info = self.db.GetSurnameIndexInfo(private, 'yearonly')
		DoTemplate('surname-index-html.tmpl', info, file, trim = True)
		return

	def do_hi(self, arg):
		'Create a name index in HTML. Abbreviation of htmlindex'
		self.do_htmlindex(arg)
		return

	def do_clearprivacy(self, arg):
		'Clear the calculated privacy of all persons in the database.'
		self.db.ClearPrivacy()
		return

	def do_showprivacy(self, arg):
		'Show the privacy status of a person.'
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			person = l[0]
			if self.db.IsPrivate(person.uniq):
				str = 'private'
			else:
				str = 'public'
			print(person.GetVitalLine(), 'is', str)
		else:
			self.PrintPersonList(l, arg)
		return

	def do_test(self, arg):
		'For testing code snippets. ToDo: delete'
		print('do_test(): ', arg)
		if arg == 'foo':
			print('foo')
		else:
			print('not foo:', arg, type(arg))
		return

if __name__ == '__main__':
	print(DhG_Shell.version)
	print('Loading database ...')
	while True:
		DhG_Shell().cmdloop()
