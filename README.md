# DhG2
## Dave's genealogy assistant v2.0

This is a rewrite of the original DhG, using python instead of perl and cleaning up a lot of the
cruft caused by major concept and design changes over the years.

DhG2 is unashamedly command-line driven. It doesn't give you a pretty interface to a hidden database.
Instead, it helps you to create structured text files called card files, one per person, then analyses
the files to produce ancestor and descendant trees and immediate family reports. It can even produce a
static HTML web site.

The card file approach means that you always have full control of your data. DhG2 only reads the existing
card files, never modifies. The only write operation is the "new" command.
Think of each card file as an old-fashioned index card, except without the physical space limit.
You edit the cardfiles with an editor of your choice, and you can keep backup copies as you please.

Recommendation: use a revision control system like git to store the cardfiles and track changes.

There is a limited GEDCOM import feature. It works for a very specific GEDCOM file created by FTM.
You have to import into an empty database, and there is no way to save the results as individual cardfiles.
After importing, the browsing and HTML generation features can be used, but of course there is no
editing capability.

### Documentation

* [Getting started](doc/GettingStarted.md)
* [Card file structure](doc/CardFormat.md)
* [Invoking DhG2](doc/Invocation.md)
* The [Configuration](doc/Configuration.md) variables
* [Command reference](doc/CommandRef.md)
* [Advanced topics](doc/Advanced.md)

### Development status

DhG2 is in a usable state with most major features implemented.

Documentation is work-in-progress:

* The built-in help is working and explains the commands and basic operation quite well.

HTML generation is fully implemented:

* Descendant trees can be generated, individually or from a list.
* Ancestor trees can be generated, individually or from a list.
* Pages for individuals files can be generated, individually or all/public.
* Name index can be generated.

### To do

There is always lots to do. :-)

* Write more documentation.
* Consider refactoring the timeline command to use the same data as HTML card, but a different template.
* OR: keep the text output as it is and implement a new command.
* Add a translation table for captions in event info. Does DhG have a list? Add Mapref -> Map reference.
* Check how Misc events are presented
* Photo statements at the file level - include photo in html?
* Syntax check of events when reading file. Currently happens on HTML card generation.

## License

Released under GPL version 3.0 - see LICENSE and gpl-3.0.txt
