# Invoking DhG2


To invoke DhG2, type the command and its optional arguments at your shell's command prompt.


Usage: /path/to/DhG2/DhG_Shell.py [options] [script-file ...]

The options are single letters preceded by a hyphen or single words preceded by two hyphens. 
If you use the single-letter variant you can group the options after a single hyphen. Example: -qe

The program accepts options and parameters as described below:

* **-h** or **--help**

	If invoked with this option, DhG2 prints information about invoking the program and then closes.

* **-v** or **--version**

	If invoked with this option, DhG2 prints the version and then closes.

* **-q** or **--quiet**

	If invoked with this option, DhG2 does not print any information messages when it starts.

* **-e** or **--exit**

	If invoked with this option, DhG2 closes after loading the database and executing the script files.

* **-c <cfgfile>** or **--config=<cfgfile>**

	If invoked with this option, DhG2 uses the specified configuration instead of the default ~/.DhG/config.
	If you use this option more than once, DhG2 uses the last one.

The **-e** and **--exit** options and the script-file arguments are currently ignored.
