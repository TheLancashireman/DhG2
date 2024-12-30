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
		'    -h --help                     print the usage text and exit\n'+\
		'    -v --version                  print the version and exit\n'+\
		'    -q --quiet                    do not print any messages at startup\n'+\
		'    -e --exit                     close after loading database and executing script files\n'+\
		'    -c cfgfile  --config=cfgfile  use cfgfile as the configuration file. Default ~/.DhG/config\n'+\
		'  If more than one cfgfile is specified, the last one is used.\n'+\
		'  The -e option and the script-file arguments are currently ignored.'
#		'  Each argument is treated as a script file.\n'+\
#		'  The commands in the scripts are executed after loading the database.\n'+\
#		'  After executing the scripts, ' + sys.argv[0] + ' drops into interactive mode.\n'+\
#		'  A quit command in one of the scripts terminates the program immediately.'

	# Message that is displayed on startup. We want to control this with "-q" so set it to None.
	intro = None

	# List of scripts, taken from the command line
	scripts = []

	# The database
	db = None

	# Configuration variables can be set in the config file
	prompt = '(DhG) '	# Parent class needs a copy

	# In the constructor, read the command line
	#
	def __init__(self):
		self.quiet = False
		self.exit = False
		dropout = False
		cfgfile = None
		super().__init__()
		try:
			(opts, args) = getopt.gnu_getopt(sys.argv[1:], "qehvc:", ["quiet", "exit", "help", "version", "config="])
		except getopt.GetoptError as err:
			# print help information and exit:
			print(err)  # will print something like "option -a not recognized"
			self.Usage()
			exit(1)
		for (opt, optarg) in opts:
			if opt == '-h' or opt == '--help':
				self.Usage()
				dropout = True
			elif opt == '-v' or opt == '--version':
				self.Version()
				dropout = True
			elif opt == '-c' or opt == '--config':
				cfgfile = optarg
			elif opt == '-q' or opt == '--quiet':
				self.quiet = True
			elif opt == '-e' or opt == '--exit':
				self.exit = True
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
		if not self.quiet:
			self.Version()
			print('Loading database ...')
			print()
			print('Type help or ? to list commands.')
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

	# Get a list of all the public commands that are available.
	# This is a list all functions that start with "do_", excluding those
	# that start with "do_zz".
	def get_commands(self):
		cmdlist = []
		for name in self.get_names():
			if name[0:3] == 'do_' and name[0:6] != 'do_zz_':
				cmdlist.append(name[3:])
		cmdlist.append('!')
		return cmdlist

	# Get a list of all the commands that match a given partial command
	# If there is an exact match, the list contains only that match
	#
	def get_matching_commands(self, keyword):
		keylen = len(keyword)
		cmdmatch = []
		for name in self.get_names():
			if name[0:3] == 'do_' and name[3:keylen+3] == keyword:
#				print('Possible match:', name[3:])
				if name[3:] == keyword:
					return [keyword]				# Exact match
				cmdmatch.append(name[3:])
		return cmdmatch

	# Preprocess the command: try to find a match for an abbreviated command.
	# If there's no match, change the line to "zz_error_no_command" followed by the abbreviation.
	# If there's more than one match, change the line to "zz_error_ambiguous_command" follwed by
	# a list of commands that match (space-separated).
	# This means that, if necessary, the emptyline() function can do something useful.
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
		cmdmatch = self.get_matching_commands(keyword)
		if len(cmdmatch) == 0:
			line = 'zz_error_no_command ' + keyword
		elif len(cmdmatch) == 1:
			line = cmdmatch[0] + ' ' + line[keylen:]
#			print('Completed command:', line)
		elif len(cmdmatch) > 1:
#			print('Ambiguous command: \''+keyword+'\'')
			line = 'zz_error_ambiguous_command'
			for m in cmdmatch:
				line = line + ' ' + m
		return line

	# Print a list of all the persons in the database.
	#
	def PrintPersonList(self, l, arg):
		if len(l) < 1:
			print('No entry', arg, 'found in the database')
		else:
			for p in l:
				print(p.GetVitalLine())		# ToDo: parameters
		return

	# Edit a card using the specified editor.
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

	# =============================
	# Print some general help text.
	#
	def PrintCommandList(self, arg):
		print('''
DhG2 responds to commands that you type at the prompt.

Type "help <command>" for documentation on a specific command.
Type "help general" for information about DhG2 command parameters.
Type "help config" for information about DhG2 configuration.

The available commands are:
		''')
		commands = self.get_commands()
		self.columnize(commands)
		print()
		return

	# =============================
	# Print some general help text.
	#
	def PrintGeneralHelp(self):
		print('''
DhG2 loads a database in the form of individual card files, one per person, into memory.
The commands provided by DhG2 perform queries and operations on the database.
With the exception of the "new" command, DhG2 never modifies your card files.
You must do that yourself using one of the editing commands.

To use DhG2, type a sequence of command lines. A command line is a command followed by additional text.
The nature of the additional text depends on the command. Many commands expect that the text
identifies a person in the database.

You can abbreviate commands using as many initial letters as necessary to uniquely specify the command.
If you type an ambiguous command, DhG2 responds with a message telling you which commands match what you
typed.
Tab completion is also possible.

For the commands that expect a parameter that identifies a person in
the database, you can specify the person by ID in the form [n] or just n.
Alternatively, you can specify the person by full or partial name.
If the name you provide matches several persons, DhG2 displays a list of matches.
You can then identify the correct person and retype the command using their ID.
		''')
		return

	# ====================================
	# Print help text for the "!" command.
	#
	def PrintPlingHelp(self):
		print('''
The "!" command invokes a program from your computer's operating system. The current working
directory (cwd) of the program is the same as the cwd in which DhG2 was originally invoked.

Usage:
   ! <command>  - Invokes <command> in a child shell.

Examples:
   !ls  - Lists the contents of the current working directory.

Note: '!' is a shortcut for "shell".
		''')
		return

	# =================================================
	# Print help text for the configuration parameters.
	#
	def PrintConfigHelp(self):
		print('''
Configuration parameters:

   cfgfile      - The name of the configuration file.
      This parameter is set on the comand line when starting DhG2. Setting it within the program has no effect.
      The default value is "~/.DhG/config".

   branch       - The current family branch, if any.
      This parameter adds an extra subdirectory level the path used by the "new" command.

   dateformat   - The date format to use in most interactive queries.
      raw      - Exactly as given in the card file.
      cooked   - Converts the symbols <, > abd ~ to text, converts Qn to the middle month with "abt."
      yearonly - Only the year.

   db_dir       - The base directory of the card database.
      This parameter must be set in the configuration file. Setting it within the program has no effect.
      There is no default value.

   depth        - Specifies the maximum depth to display for interactive trees.

   editor       - Specifies the name of the program to use for the "edit" command.

   generate     - Specifies the privacy for HTML generation.
      public  - Persons designated as "private" are omitted.
      all     - All persons are included.
		
   html_dir     - The directory in which to place the generated HTML files.

   prompt       - The prompt to display when DhG2 can accept a command.

   server_path  - The base path to use for local links in the generated HTML files.

   text-suffix  - The suffix of transcript files that can be included verbatim in generated HTML files.

   text_path    - The directory in which text transcripts can be found.
      DhG2 searches for files in all subdirectories in of this directory.

   tmpl_path    - The list of directories to search for templates.
      The individual directories are separated using ":".
		''')
		return

	# ===================================
	# Report the ambiguous command error.
	#
	def do_zz_error_ambiguous_command(self, arg):
		'''
zz_error_ambiguous_command is an internal command for reporting ambiguous command abbreviations. Not for normal use.
		'''
		print('Ambiguous command. Possible matches are: ', arg)
		return

	# =====================================
	# Report the no matching command error.
	#
	def do_zz_error_no_command(self, arg):
		'''
zz_error_no_command is an internal command for reporting unknown command error. Not for normal use.
		'''
		print('DhG2 has no command that matches "'+arg+'".')
		return

	# ================================
	# An internal command for testing.
	#
	def do_zz_test(self, arg):
		'''
zz_test is an internal command for testing purposes. Not for normal use.
		'''
		print('do_zz_test(): ', arg)
		zzz = os.path.dirname(__file__)+'/templates'
		print(zzz)
		return

	# =====================================
	# Implementation of the "help" command.
	#
	def do_help(self, arg):
		'''
The "help" command provides built-in documentation.

Usage:
   help            - Provides a list of the available commands.
   help <command>  - Provides help for the specified command.
   help general    - Provides some general documentation.
   help config     - Provides information about configuration parameters.
		'''
		if arg == None or arg == '':
			self.PrintCommandList(arg)
			return
		if arg == 'general':
			self.PrintGeneralHelp()
			return
		if arg == 'config':
			self.PrintConfigHelp()
			return
		if arg == '!':
			self.PrintPlingHelp()
			return

		cmdmatch = self.get_matching_commands(arg)
		if len(cmdmatch) == 0:
			print('DhG2 has no command that matches "'+arg+'".')
		else:
			for cmd in cmdmatch:
				super().do_help(cmd)
		return

	# =====================================
	# Implementation of the "quit" command.
	#
	def do_quit(self, arg):
		'''
The "quit" command closes DhG2.

Usage:
   quit  - Closes DhG2. Parameters are ignored.
		'''
		exit(0)

	# ====================================
	# Implementation of the "set" command.
	#
	def do_set(self, arg):
		'''
The "set" command sets a configuration parameter.

Usage:
   set                 - Lists all the configuration parameters and their values.
   set <name>=<value>  - Sets the configuration parameter <name> to <value>.

Spaces immediately before and after the '=' sign are ignored.

Type "help config" to see a list of the configuration parameters.
		'''
		if arg == '':
			Config.Print()
			return
		if not Config.SetParameter(arg):
			print('Error : invalid syntax for the set command')
		return

	# ======================================
	# Implementation of the "reload" command
	#
	def do_reload(self, arg):
		'''
The "reload" command reloads the entire database from the card files into memory.

Normally you should not need to do this. The command is useful if you
edit many card files outside of a running DhG2 process.
Hint: if you edit a single card file it might be quicker just to open
the file within DhG2 and close it without making changes.

Usage:
   reload  - Reloads the database. Parameters are ignored.
		'''
		self.db.Reload()
		return

	# ======================================
	# Implementation of the "unused" command
	#
	def do_unused(self, arg):
		'''
The "unused" command lists all the unique IDs that are not used, up to the highest known ID that is used.

Usage:
   unused  - Lists all the IDs that are not used in the database. Parameters are ignored.
		'''
		l = self.db.GetUnused()
		for i in l:
			print('['+str(i)+']')
		return

	# =====================================
	# Implementation of the "list" command.
	#
	def do_list(self, arg):
		'''
The "list" command lists all the persons in the database. It ignores any parameters that you give.

Usage:
   list  - Lists all the persons in the database. Parameters are ignored.
		'''
		self.do_find('')
		return

	# =====================================
	# Implementation of the "find" command.
	#
	def do_find(self, arg):
		'''
The "find" command displays a list of persons that match the given parameters.

Usage:
   find <person>  - displays a list of matching persons.

Note: "search" and "find" have identical behaviour.
		'''
		l = self.db.GetMatchingPersons(arg)
		for p in l:
			print(p.GetVitalLine())		# ToDo: parameters
		return

	# =======================================
	# Implementation of the "search" command.
	#
	def do_search(self, arg):
		'''
The "search" command displays a list of persons that match the given parameters.

Usage:
   search <person>  - displays a list of matching persons.

Note: "search" and "find" have identical behaviour.
		'''
		self.do_find(arg)
		return

	# =========================================
	# Implementation of the "timeline" command.
	#
	def do_timeline(self, arg):
		'''
The "timeline" command displays the timeline for the specified person.

Usage:
   timeline <person> - Displays the timeline for <person>.
		'''
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			tl = l[0].GetTimeline()
			for txt in tl:
				print(txt)
		else:
			self.PrintPersonList(l, arg)
		return

	# ===================================
	# Implementation of the "tl" command.
	#
	def do_tl(self, arg):
		'''
The "tl" command displays the timeline for the specified person.
"tl" is an abbreviation for "timeline".

Usage:
   tl <person> - Displays the timeline for <person>.
		'''
		self.do_timeline(arg)
		return

	# ===================================
	# Implementation of the "vi" command.
	#
	def do_vi(self, arg):
		'''
The "vi" command edits a person's card file using the vi editor.
The vi program must be present in your shell's search path.

Usage:
   vi <person>  - Invokes vi to edit the person's card file.
		'''
		self.EditCard('vi', arg)
		return

	# ====================================
	# Implementation of the "vim" command.
	#
	def do_vim(self, arg):
		'''
The "vim" command edits a person's card file using the vim editor.
The vim program must be present in your shell's search path.

Usage:
   vim <person>  - Invokes vim to edit the person's card file.
		'''
		self.EditCard('vim', arg)
		return

	# =====================================
	# Implementation of the "edit" command.
	#
	def do_edit(self, arg):
		'''
The "edit" command edits a person's card file using your configured editor.

Usage:
   edit <person>  - Invokes your configured editor to edit the person's card file.
		'''
		self.EditCard(Config.Get('editor'), arg)
		return

	# ====================================
	# Implementation of the "new" command.
	#
	def do_new(self, arg):					# Refactor this function
		'''
The "new" command creates a card file for a new person and automatically loads the new
file into memory.
DhG2 automatically assigns a unique ID for the person.
The parameter is the full name of the person as normally written.

Usage:
   new <name>  - Create a new person in the database.

Example: The command "new Kevin Philip Bong" creates a card file called KevinPhilipBong-nnn.card in the
subdirectory Bong (optionally in the current branch subdirectory) of your database. nnn is the unique ID
that is assigned autonatically.

See also the configuration parameters "branch", "father" and "mother". Type "help config" for information.
		'''
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

	# =======================================
	# Implementation of the "family" command.
	#
	def do_family(self, arg):
		'''
The "family" command displays the immediate family (parents, siblings and children) of the specified person.

Usage:
   family <person>  - Displays a person's immediate family.
		'''
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			fam = self.db.GetFamily(l[0].uniq)
			DoTemplate('family-text.tmpl', fam, None)
		else:
			self.PrintPersonList(l, arg)
		return

	# ==========================================
	# Implementation of the "descendants" command.
	#
	def do_descendants(self, arg):
		'''
The "descendants" command displays a descendants tree for the specified person.
The depth of the tree is limited to the value of the "depth" configuration parameter.

Usage:
   descendants <person>  - Displays a descendants tree for <person>.
		'''
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

	# ==========================================
	# Implementation of the "ancestors" command.
	#
	def do_ancestors(self, arg):
		'''
The "ancestors" command displays an ancestry tree (also known as an Ahnentafel) for the specified person.
The depth of the tree is limited to the value of the "depth" configuration parameter.

Usage:
   ancestors <person>  - Displays an ancestors tree for <person>.
		'''
		l = self.db.GetMatchingPersons(arg)
		if len(l) == 1:
			anc = self.db.GetAncestorsObsolete(l[0].uniq)
			DoTemplate('ancestor-tree-text.tmpl', anc, None)
		else:
			self.PrintPersonList(l, arg)
		return

	# ======================================
	# Implementation of the "heads" command.
	#
	def do_heads(self, arg):
		'''
The "heads" command displays a list of all the patriarchs and/or matriarchs in the database.
A patriarch (male) or matriarch (female) is defined as a person whose parents AND whose spouse's parents
are not recorded in the database. The command accepts a single parameter.

Usage:
   heads male    - Displays a list of all patriarchs in the database.
   heads female  - Displays a list of all matriarchs in the database.
   heads both    - Displays a list of all patriarchs and matriarchs in the database.
   heads         - Equivalent to "heads both"
		'''
		self.db.ListHeads(arg)
		return

	# =======================================
	# Implementation of the "verify" command.
	#
	def do_verify(self, arg):
		'''
The "verify" command verifies that all persons that are referenced in the database actually
exist and have the same name as the reference. The verification applies to parents and spouses,
but not to other people like witnesses, where the name given in the record might differ from
their official name.

Usage:
   verify  -- Verify the person references in the database. Parameters are ignored.
		'''
		if self.db.VerifyRefs() == 0:
			print('Verification complete; no errors')
		return

	# ==========================================
	# Implementation of the "gedimport" command.`
	#
	def do_gedimport(self, arg):
		'''
The "gedimport" command imports a GEDCOM file into an empty database.
The command allows you to use the query and HTML generation features of DhG2 on the contents
of an existing GEDCOM file. However, importing a GEDCOM file into an existing database is not
supported. Neither is it possible to save the imported database into a set of card files.

Usage:
   gedimport <gedcomfile>  - Import <gedcomfile> into an empty database.

Warning: If you use the "new" command after importing a GEDCOM file, the new person is
added to the database as a card file. This means that you can no longer use the "gedimport"
command unless you manually delete the card files that you created.

Caveat: The "gedimport" command was written with a specific GEDCOM file in mind. It might not
work with other GEDCOM files from different sources.
		'''
		self.db.ImportGedcom(arg)
		return

	# ======================================
	# Implementation of the "shell" command.
	#
	def do_shell(self, arg):
		'''
The "shell" command invokes a program from your computer's operating system. The current working
directory (cwd) of the program is the same as the cwd in which DhG2 was originally invoked.

Usage:
   shell <command>  - Invokes <command> in a child shell.

Examples:
   shell ls  - Lists the contents of the current working directory.

Note: '!' is a shortcut for "shell".
		'''
		os.system(arg)
		return

	# ================================================
	# Implementation of the "htmldescendants" command.
	#
	def do_htmldescendants(self, arg):
		'''
The "htmldescendants" command creates a descendants tree in HTML format for the specified person or persons.
The HTML file is called trees/FULLNAME-ID-descendants.html and is placed in the configured HTML directory.

Usage:
   htmldescendants <person>   - Creates a descendants tree in HTML for <person>.
   htmldescendants @filename  - Creates a descendants tree in HTML for each person listed in the specified file.
		'''
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

	# ===================================
	# Implementation of the "hd" command.
	#
	def do_hd(self, arg):
		'''
The "hd" command creates a descendants tree in HTML format for the specified person or persons.
The HTML file is called trees/FULLNAME-ID-descendants.html and is placed in the configured HTML directory.
"hd" is an abbreviation for "htmldescendants".

Usage:
   hd <person>   - Creates a descendants tree in HTML for <person>.
   hd @filename  - Creates a descendants tree in HTML for each person listed in the specified file.
		'''
		self.do_htmldescendants(arg)
		return

	# ==============================================
	# Implementation of the "htmlancestors" command.
	#
	def do_htmlancestors(self, arg):
		'''
The "htmlancestors" command creates an ancestors tree (also known as an Ahnentafel) in HTML format
for the specified person or persons.
The HTML file is called trees/FULLNAME-ID-ancestors.html and is placed in the configured HTML directory.

Usage:
   htmlancestors <person>   - Creates an ancestor tree in HTML for <person>.
   htmlancestors @filename  - Creates an ancestor tree in HTML for each person listed in the specified file.
		'''
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

	# ===================================
	# Implementation of the "ha" command.
	#
	def do_ha(self, arg):	# Abbreviated command
		'''
The "ha" command creates an ancestors tree (also known as an Ahnentafel) in HTML format
for the specified person or persons.
The HTML file is called trees/FULLNAME-ID-ancestors.html and is placed in the configured HTML directory.
"ha" is an abbreviation for "htmlancestors".

Usage:
   ha <person>   - Creates an ancestor tree in HTML for <person>.
   ha @filename  - Creates an ancestor tree in HTML for each person listed in the specified file.
		'''
		self.do_htmlancestors(arg)
		return

	# =========================================
	# Implementation of the "htmlcard" command.
	#
	def do_htmlcard(self, arg):
		'''
The "htmlcard" command creates an information card in HTML format for the specified person or persons.
The HTML file is called cards/SURNAME/FULLNAME-ID.html and is placed in the configured HTML directory.

Usage:
   htmlcard <person>  - Creates an HTML card file for <person>.
   htmlcard @all      - Creates HTML card files for all persons in the database.
   htmlcard @public   - Creates HTML card files for all persons that are not designated as private. 
		'''
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

	# ===================================
	# Implementation of the "hc" command.
	#
	def do_hc(self, arg):
		'''
The "hc" command creates an information card in HTML format for the specified person or persons.
The HTML file is called cards/SURNAME/FULLNAME-ID.html and is placed in the configured HTML directory.
"hc" is an abbreviation for "htmlcard".

Usage:
   hc <person>  - Creates an HTML card file for <person>.
   hc @all      - Creates HTML card files for all persons in the database.
   hc @public   - Creates HTML card files for all persons that are not designated as private. 
		'''
		self.do_htmlcard(arg)
		return

	# ==========================================
	# Implementation of the "htmlindex" command.
	#
	def do_htmlindex(self, arg):
		'''
The "htmlindex" command creates an index to the HTML card files in HTML format.

Usage:
   htmlindex @all     - Creates an HTML index containing all persons in the database.
   htmlindex @public  - Creates and HTML index containing all persons that are not designated as private.
		'''
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

	# ===================================
	# Implementation of the "hi" command.
	#
	def do_hi(self, arg):
		'''
The "hi" command creates an index to the HTML card files in HTML format.
"hi" is an abbreviation for "htmlindex".

Usage:
   hi @all     - Creates an HTML index containing all persons in the database.
   hi @public  - Creates and HTML index containing all persons that are not designated as private.
		'''
		self.do_htmlindex(arg)
		return

	# =============================================
	# Implementation of the "clearprivacy" command.
	#
	def do_clearprivacy(self, arg):
		'''
The "clearprivacy" command clears the calculated privacy of all persons in the database.
Calculating the privacy status for a large database is a time-consuming process, so once
calculated the value is stored. However, explicitly changing a person's privacy by setting
the person to private or deleting their death record might affect other persons' status
too.

Usage:
   clearprivacy  - Clears the calculated privacy status for the whole database. Parameters are ignored.
		'''
		self.db.ClearPrivacy()
		return

	# ============================================
	# Implementation of the "showprivacy" command.
	#
	def do_showprivacy(self, arg):
		'''
The "showprivacy" command shows the privacy status of a specified person.

Usage:
   showprivacy <person>  - Shows the privacy status for <person>.
		'''
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

if __name__ == '__main__':
	while True:
		DhG_Shell().cmdloop()
