# Getting started

This guide assumes you are using a unixy operating system like Linux.

## Installation

You need to ensure that python3 is installed. This is normally standard for all modern Linux distributions.
You also need to install the "jinja2" template library for python3. The package is called "python3-jinja2"
or something similar. Use your package manager to install it.

Open a terminal window and change the current directory to somewhere suitable.

If your PC has git installed, you can clone the Codeberg repository. Change the current directory to
a suitable place and type "git clone https://codeberg.org/TheLancashireman/DhG2.git" in the terminal
window. This should create a new directory called DhG2 that contains the application. Using git is
the simplest way, because to update DhG2 you only need to change directory to the DhG2 directory
and type "git pull".

If git isn't installed, download and install an archive from
[https://codeberg.org/TheLancashireman/DhG2](https://codeberg.org/TheLancashireman/DhG2).
There's a "..." button on the right, near the top. Click the option to download a ZIP file, or TAR.GZ.
Unpack the downloaded file into somewhere suitable. Unfortunately, the downloaded archives unpack to
"dhg2" instead of "DhG2" so either rename the directory or take the change into account in later instructions.

## Setup

Create a directory in your home directory called .DhG and copy the minimal.cfg file from the DhG2 installation
to "~/.DhG/config". Edit the new file; You need to change the value of the db_dir variable so that it
specifies the location of the directory of your card file database.

You can place your database wherever you like. Create the directory before running DhG.

In addition, the default "editor" setting might not suit your personal taste. Choose a text editor that
you're comforable with. "gedit" or "nano" might be better than the default "vi" for many people.
Don't use a word processor unless you're sure that it can save in text format without destroying
the file structure.

You should now be able to run DhG2. Type "/path/to/DhG2/DhG_Shell.py".

### Hint

It's useful if the current working directory of DhG2 is your database directory. You can create a
shell script to ensure this. The script will contain something like:

```text
#!/bin/sh
cd /path/to/your/database
exec /path/to/DhG2/DhG_Shell.py $@
```

If you call this script "DhG2" and place it in your search path, then simply typing "DhG2" in a terminal
window will start DhG2 in the database.

## Adding individuals to the database

The easiest way to add a new person to your database is by using the "new" command. Let's say that
your research so far has discovered that your grandmother Jill Pewty had a brother called Jack Pewty.
Furthermore, their parents were Arthur Pewty and Martha, whose maiden name was Gumby.

Type "new Arthur Pewty" at the DhG2 command prompt. DhG2 tells you the name and unique identifier,
for example "Arthur Pewty [1]".

Type "new Martha Gumby" at the DhG2 command prompt. DhG2 tells you the name and unique identifier,
for example "Martha Gumby [2]".

To create records for Jack Pewty and Jill Pewty you could just use the "new" command and then edit their
files to add the parents. But there's a more convenient way:

* Type "set father = Arthur Pewty [1]"
* Type "set mother = Martha Gumby [2]"

Now, when you use "new" to create records for Jack Pewty and Jill Pewty, their parents are already assigned.

You can use the descendants command to see the family tree: type "d Arthur Pewty".

Don't forget to set the father and mother parameters back to nothing afterwards, otherwise all new records will
appear to be children of Arthur and Martha.

## Adding information to existing individuals

To add information to an individual's record, use the "edit" command. This invokes the text editor that
you can configured in the configuration file.

There's a guide to writing a card file [here](doc/CardFormat.md).

You can add as much or as little information as you like. As a minimum, it's recommended to have a birth
record with a date so that DhG2 can place children of a partnership in the correct order. Also a death record
for the people who you know or can assume are deceased. For people who are still alive, delete the death
record, comment it out or place it after an EOF marker.

If you don't know the date of birth, make an educated guess and use the "~" symbol. If you don't know
the date of death, use "?".

It's also useful to add a marriage or partnership record. DhG2 infers a partnership from the father and
mother lines of the children. An explicit record is useful for childless couples.

## Querying the database

The "descendants" command shows all the descendants of an individual. As your database grows, this might
become too large to see in one screen. You can limit the depth by typing "set depth=n". The "set" command
changes the value of a configuration parameter until you close DhG2.

The "ancestors" command shows all the ancestors of an individual. The "depth" setting affects this tree too.

The "list" command lists all the individuals in the database. The command gets less useful as your database
grows.

The "find" command lists all the individuals whose names contain the strings that you supply in the arguments.
For example, in your Pewty database of four people, "find ji" finds Jill, whereas "find j" finds both Jack and Jill.

The "family" command shows the immediate relatives (parents, siblings and children) of an individual.

The full set of commands is available in the built-in documentation by using the "help" command. There's also
full documentation in the [command reference](CommandReference.md).

## Specifying an individual

As your database grows, you'll find that using name to identify an individual is no longer possible.

The commands that expect an individual as a parameter use the search function as described above for the
"find" command. If there's a unique match, the command is performed for that individual. If there are
several indivuals that match the parameters, the command lists them along with their identifiers.

For example, if you type "e j pew", the command lists both Jack and Jill. You can then retype the command
using the unique identifier: "e 3" or "e 4", depending on whether you want to edit Jack or Jill.

You can give the unique identifier as a bare number or in (square) brackets exactly as displayed by the
original command. If you give a partial name and an assigned identifer in brackets, the command ignores the
name and uses the identifier. However, if you give a partial name and a bare number then the number is treated
as part of the name and there is unlikely to be a match.
