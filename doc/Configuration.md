# Configuration

DhG2 has an internal set of configuration variables that it uses to modify its functionality.

The configuration file contains a list of statements that assign initial values to internal variables used
by DhG2.

You use the "set" command at the prompt to change the values during a DhG2 session. The values assigned
by the "set" command are discarded when you close DhG2.

The "set" command is described in the [command reference](CommandRef.md).

## The configuration file

The configuration file is a text file whose name and location you can provide when you invoke DhG2.
If no file is explicitly given, DhG2 uses ~/.DhG/config.

The configuration file is a plain text file. DhG2 ignores blank lines and lines that start with a
"#" character, so you can add comments.

Assignments are lines of the form "\<name\> = \<value\>" where \<name\> is the name of the variable and
\<value\> is the value you wish to assign.

Leading and trailing spaces are removed from both name and value.

Optionally, you can surround the value with quotation marks. This is useful if you want a leading
or trailing space in the value.

The name of the variable can be any sequence of characters. DhG2 doesn't check the name, so you can define
your own variables. The complete set of variables gets passed to the template engine.

There are two mandatory configuration variables: db_dir and tmpl_path. The rest are optional and have
reasonable default values.

There's an example configuration file example.cfg in the DhG2 installation directory.

## Configuration variables

The configuration variables that control the general functionality of DhG2 are described in alphabetical
order in the following sections.

### branch

The branch variable specifies which subdirectory of the database directory is to be used for new cards
created by the "new" command. In effect, using branch creates an extra level subdirectory level
in the database, which might be useful if you research several different but interconnected
family trees.

If the branch variable is empty or not set, the surname directories are placed directly under the
database directory.

### cfgfile

The cfgfile variable contains the name and location of the configuration file. The configuration
file is only read when DhG2 starts, so setting it with the "set" command makes little sense.

### dateformat

The dateformat variable controls what date format DhG2 uses for interactive queries.

Recognised values are raw, cooked, yearonly. The default is raw.

### db_dir

The db_dir variable specifies the location of the database of card files. DhG2 searches for card files
in the entire directory tree that is rooted at db_dir.

db_dir **must** be set in the configuration file, otherwise DhG2 cannot load the database.

You can change db_dir using the "set" command, but if you do, you must reload the database to
synchronise DhG2 with the new database, otherwise the unique identifiers of new individuals
might be assigned incorrectly. It is therefore not recommended to change db_dir in that way.

### depth

The maximum depth that DhG2 descends when displaying family trees. You must set the value of
this parameter to a number, otherwise you might get strange error messages.

The default value is 999999.

### editor

The editor variable specifies which text editor DhG2 invokes when you use the "edit" command.

The default editor is vi. Choose an editor that you are comfortable with. On a Linux host you
might choose nano or gedit, perhaps.

DhG2 is suspended while the editor is running. If the editor runs in the same terminal window
(e.g. nano) this behaviour is normal. If the editor opens a new window (e.g. gedit) then DhG2
displays a message "Editing \<filename\>". The prompt reappears when you close the editor.

### father

The father variable is used by the "new" command to assign a parent to a new individual.

The default value is not set.

If the father variable is not set or is an empty string, the "new" command does not assign a father.

### mother

The mother variable is used by the "new" command to assign a parent to a new individual.

The default value is not set.

If the mother variable is not set or is an empty string, the "new" command does not assign a mother.

### prompt

The prompt variable is what DhG2 displays when is is ready to accept a command.

The default value is "(DhG) ".

### tmpl_path

The tmpl_path variable is a list of locations that DhG2 searches for templates. The locations
must be separated by colon (':') characters.

Normally, the template directly in the DhG2 installation is the last in the list. If you have any
customised templates, put them in a directory that appears before the installation templates.

tmpl_path is a mandatory variable. If it is not set, many of the features of DhG2 do not work.

## Configuration variables for HTML generation

The variables described in this section only affect the generation of HTML files.

### card_path

The card_path variable controls where DhG2 places the generated HTML card files for individuals.

If card_path is not set or is empty, the files are placed into a cards/ subdirectory of the
the directory specified by html_dir.

### generate

The generate variable controls how DhG2 generates HTML pages. The recognised values are
"public" and "private".

If generate is set to "public", DhG2 generates HTML files for publication. Individuals that are
determined to be "private" are omitted from the generated files.

If generate is set to "private", a complete set of HTML files is generated, including all living
individuals and their immediate relatives.

### html_dir

The html_dir variable controls where DhG2 places the generated HTML files.

The surname index is placed directly into this directory. Ancestor and descendant trees are
placed in a trees/ subdirectory. HTML card files for indiviuals are placed in a cards/ subdirectory
unless card_path is set.

If html_dir is not set, DhG2 places the HTML files in the current working directory. If the
cwd is the same as the database, the generated HTML files mingle with the cards database.

### server_path

The server_path variable specifies the root URL of the family tree directory as seen from
the HTTP server. It is used in order to generate correct links in the HTML pages.

### text-suffix

The text-suffix variable specifies the suffix ("extension") of transcript files to consider
for inclusion in generated HTML cards.

### text_path

The text_path variable specifies where DhG2 searches for textual transcripts of documents.
