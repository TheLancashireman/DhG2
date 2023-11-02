# DhG2
## Dave's genealogy assistant v2.0

This is a rewrite of the original DhG, using python instead of perl and cleaning up a lot of the
cruft caused by major concept and design changes over the years.

The program is now in a usable state with most major features implemented.

HTML generation is partially implemented:
* Descendant trees should be working for individuals; lists not supported yet.
* Card files can be generated.
* Ancestor trees, name index etc. still to do.
* Publicity of people is not implemented - HTML generation includes everyone, even when private.

There is a limited GEDCOM import feature that works for a very specific GEDCOM file created by FTM.
You have to import into an empty database, and there is no way to save the results as individual cards.

Released under GPL version 3.0 - see LICENSE and gpl-3.0.txt

The program is unashamedly command-line driven. It doesn't give you a pretty interface to a hidden database.
Instead, it helps you to create structured text files, one per person, then analyses the files to produce ancestor
and descendant trees and immediate family reports. It can even produce a static HTML web site.

The text file approach means that you always have full control of your data

## To do

There is always lots to do. :-)

* Consider refactoring the timeline command to use the same data ad HTML card, but a different template.
* OR: keep the text output as it is and implement a new command.
* Add a privacy filter.
* Add a translation table for captions in event info. Does DhG have a list? Add Mapref -> Map reference.
* Read transcripts from transcript file (some types)
* Check how Misc events are presented
* Process notes and other information at the file level. Nickname, Private, Note etc. Photo?
