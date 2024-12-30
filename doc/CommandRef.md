# Command reference

DhG2 commands are described here in alphabetical order.

You can abbreviate commands using sufficient leading characters to identify the command uniquely. If
what you type is not unique, DhG2 gives you a list of the commands that match.

When a command expects a *PERSON* as its parameter, you can specify the person by their
unique identifier, either as a bare number or enclosed in brackets.

You can also specify a person by parts of a name. Any person whose name contains all the specified
parts is considered as a match. If there is more than one match, the command displays a list of
matching persons along with their identifiers and dates. You can then retype the command using
the identifier.

## ancestors

### Synopsis

The **ancestors** command displays an ancestry tree (also known as an Ahnentafel) for the specified person.

The depth of the tree is limited to the value of the **depth** configuration parameter.

### Usage

* **ancestors** *PERSON*
	* Displays an ancestors tree for the specified person.

## clearprivacy

### Synopsis

The **clearprivacy** command clears the calculated privacy of all persons in the database.

Calculating the privacy status for every person in a large database can be a time-consuming process,
so the value for each individual is only calculated when needed. The calculated value is then
stored and used when subsequently needed.

However, explicitly changing a person's privacy by setting the person to private or deleting their
death record might affect other persons' status too. The **clearprivacy** command clears and the
caclulated privacy values and forces a recalculation the next time they are needed.

### Usage

* **clearprivacy**
	* Clears the calculated privacy status for the whole database. Parameters are ignored.

## descendants

### Synopsis

The **descendants** command displays a descendants tree for the specified person.

The depth of the tree is limited to the value of the **depth** configuration parameter.

### Usage

* **descendants** *PERSON*
	* Displays a descendants tree for the specified person.

## edit

### Synopsis

The **edit** command invokes your configured editor to edit the card file of the specified person.

### Usage

* **edit** *PERSON*
	* Edits the card file of the specified person.

## family

### Synopsis

The **family** command displays the immediate family - parents, siblings and children - of the specified person.

### Usage

* **family** *PERSON*
	* Displays the immediate family of the specified person.

## find

### Synopsis

The **find** command displays a list of persons that match the given parameters.

**search** is an alias for **find**.

### Usage

* **find** *PERSON*
	* Displays a list of persons that match the parameters.

## gedimport

### Synopsis

The **gedimport** command imports a GEDCOM file into an empty database.
The command allows you to use the query and HTML generation features of DhG2 on the contents
of an existing GEDCOM file. However, importing a GEDCOM file into an existing database is not
supported. Neither is it possible to save the imported database into a set of card files.

If you use the **new** command after importing a GEDCOM file, the new person is
added to the database as a card file. This means that you can no longer use the **gedimport**
command unless you manually delete the card files that you created.

Caveat: The **gedimport** command was written with a specific GEDCOM file in mind. It might not
work with other GEDCOM files from different sources.

### Usage

* **gedimport** *GEDCOMFILE*
	* Imports the specified file into an empty database.

## ha

**ha** is an alias for **htmlancestors**.

## hc

**hc** is an alias for **htmlcard**.

## hd

**hd** is an alias for **htmldescendants**.

## heads

### Synopsis

The **heads** command displays a list of all the patriarchs and/or matriarchs in the database.
A patriarch (male) or matriarch (female) is defined as a person whose parents AND whose spouse's parents
are not recorded in the database.

### Usage

* **heads male**
	* Displays a list of all patriarchs in the database.
* **heads female**
	* Displays a list of all matriarchs in the database.
* **heads both**
	* Displays a list of all patriarchs and matriarchs in the database.
* **heads**
	* Equivalent to **heads both**

## help

### Synopsis

The **help** command provides the built-in documentation.

### Usage

* **help**
	* Provides a list of the available commands.
* **help** *command*
	* Provides help for the specified command.
* **help general**
	* Provides some general documentation.
* **help config**
	* Provides information about configuration parameters.

## hi

**hi** is an alias for **htmlindex**.

## htmlancestors

### Synopsis

The **htmlancestors** command creates an ancestors tree (also known as an Ahnentafel) in HTML format
for the specified person or persons.
The HTML file is called `FULLNAME-ID-ancestors.html` and is placed in the `trees/` subdirectory
of the configured HTML directory.

**ha** is an alias for **htmlancestors**.

### Usage

* **htmlancestors** *PERSON*
	* Creates an ancestor tree in HTML for the specified person.
* **htmlancestors** &#64;*FILENAME*
	* Creates an ancestor tree in HTML for each person listed in the specified file.

## htmlcard

### Synopsis

The **htmlcard** command creates an information card in HTML format for the specified person or persons.
The HTML file is called `SURNAME/FULLNAME-ID.html` and is placed in the `cards\` subdirectory
of the configured HTML directory.

**hc** is an alias for **htmlcard**.

### Usage

* **htmlcard** *PERSON*
	* Creates an HTML card file for the specified person.
* **htmlcard @all**
	* Creates an HTML card file for every person in the database.
* **htmlcard @public**
	* Creates an HTML card file for every person that is not designated as private. 

## htmldescendants

### Synopsis

The **htmldescendants** command creates a descendants tree in HTML format for the specified person or persons.
The HTML file is called `FULLNAME-ID-descendants.html` and is placed in the `trees/` subdirectory
of the configured HTML directory.

**hd** is an alias for **htmldescendants**.

### Usage

* **htmldescendants** *PERSON*
	* Creates a descendants tree in HTML for the specified person.
* **htmldescendants** &#64;*filename*
	* Creates a descendants tree in HTML for each person listed in the specified file.

## htmlindex

### Synopsis

The **htmlindex** command creates an index to the HTML card files in HTML format.

**hi** is an alias for **htmlindex**.

### Usage

* **htmlindex @all**
	* Creates an HTML index containing all persons in the database.
* **htmlindex @public**
	* Creates and HTML index containing all persons that are not designated as private.

## list

### Synopsis

The **list** command lists all the persons in the database. It ignores any parameters that you type.

**list** is equivalent to **find** with no parameters.

### Usage

* **list**
	* Lists all the persons in the database.

## new

### Synopsis

The **new** command creates a card file for a new person and loads the new
file into memory.

The *NAME* parameter is the full name of the person as normally written.
DhG2 automatically assigns a unique ID for the person.

The new file is placed into the appropriate surname directory in the database, optionally under
the current *branch*. See the [configuration guide](Configuration.md) for details.

### Usage

* **new** *NAME*
	* Create a new person in the database.

### Example

* **new** Kevin Philip Bong
	* creates a new file for a person named Kevin Philip Bong.

## quit

### Synopsis

The **quit** command closes DhG2.

### Usage

* **quit**
	* Closes DhG2. Parameters are ignored.

## reload

### Synopsis

The **reload** command reloads the entire database from the card files into memory.

Normally you should not need to do this. The command is useful if you
edit many card files outside of a running DhG2 process.

Hint: if you edit a single card file it might be quicker just to open
the file within DhG2 and close it without making changes.

### Usage

* **reload**
	* Reloads the database. Parameters are ignored.

## search

**search** is an alias for **find**.

## set

### Synopsis

The **set** command sets the configuration variable *NAME* to *VALUE*.

*NAME* can be any sequence of characters starting with a non-space character, **except** "cfgfile".

Spaces immediately before and after the '=' sign are ignored, as are any trailing spaces at the end of the line.
Quotation marks around *VALUE* are removed after the leading and trailing spaces have been removed, so if you
want to set a value containing a leading or trailing space, use quotation marks.

If used without parameters, **set** displays the name of the configuration file followed by all the
configuration variables that have been set, in alphabetical order.

See the [configuration guide](Configuration.md) for details of the configuration variables that DhG2 uses.

### Usage

* **set** *NAME* = *VALUE*
	* Sets the configuration variable *NAME* to *VALUE*.
* **set**
	* Displays all the configuration variables and their values.

## shell

### Synopsis

The **shell** command invokes a program from your computer's operating system using the specified *COMMANDLINE*.
The current working directory (cwd) of the program is the same as the cwd in which DhG2 was originally invoked.

*COMMANDLINE* is passed to the shell interpreter exactly as you type it, so you can use output and input
redirection.

**!** is an alias for **shell**.

### Usage

* **shell** *COMMANDLINE*
	* Executes *COMMANDLINE* in a shell.

## showprivacy

### Synopsis

The **showprivacy** command shows the privacy status of a specified person.

### Usage

* **showprivacy** *PERSON*
	* Shows the privacy status for the specified person.

## timeline

### Synopsis

The **timeline** command displays the timeline for the specified person.

### Usage

* **timeline**  *PERSON*
	* Displays the timeline for the specified person.

## tl

**tl** is an alias for **timeline**.

## unused

### Synopsis

The **unused** command provides a list of all the unused unique identifiers up to the highest known
identifier that is used.

### Usage

* **unused**
	* Lists all the unique identifiers that are not used in the database. Parameters are ignored.

## verify

### Synopsis

The **verify** command verifies that all persons that are referenced in the database actually
exist and have the same name as the reference. The verification applies to parents, spouses and
partners but not to other people like witnesses, where the name given in the record might differ from
their official name.

### Usage

## vi

### Synopsis

The **vi** command edits a person's card file using the `vi` editor.
The `vi` program must be present in your shell's search path.

### Usage

* **vi** *PERSON*
	* Invokes `vi` to edit the specified person's card.

## vim

### Synopsis

The **vim** command edits a person's card file using the `vim` editor.
The `vim` program must be present in your shell's search path.

### Usage

* **vim** *PERSON*
	* Invokes `vim` to edit the specified person's card.

## !

**!** is an alias for **shell**.
