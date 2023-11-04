# DhG2
## Dave's genealogy assistant v2.0

This is a rewrite of the original DhG, using python instead of perl and cleaning up a lot of the
cruft caused by major concept and design changes over the years.

DhG2 is unashamedly command-line driven. It doesn't give you a pretty interface to a hidden database.
Instead, it helps you to create structured text files called cardfiles, one per person, then analyses
the files to produce ancestor and descendant trees and immediate family reports. It can even produce a
static HTML web site.

The cardfile approach means that you always have full control of your data. DhG2 only reads the
cardfiles, never writes. Think of each cardfile as an old-fashioned index card, except without the
physical space limit. You edit the cardfiles with an editor of your choice, and you can keep backup
copies as you please.

Recommendation: use a revision control system like git to store the cardfiles and track changes.

There is a limited GEDCOM import feature. It works for a very specific GEDCOM file created by FTM.
You have to import into an empty database, and there is no way to save the results as individual cardfiles.
After importing, the browsing and HTML generation features can be used, but of course there is no
editing capability.

### Development status

DhG2 is in a usable state with most major features implemented.

HTML generation is partially implemented:
* Descendant trees can be generated, individually or from a list.
* Card files can be generated, individually or all/public.
* Ancestor trees, name index etc. still to do.

### To do

There is always lots to do. :-)

* Consider refactoring the timeline command to use the same data ad HTML card, but a different template.
* OR: keep the text output as it is and implement a new command.
* Add a translation table for captions in event info. Does DhG have a list? Add Mapref -> Map reference.
* Check how Misc events are presented
* Photo statements at the file level - include photo in html?
* Syntax check of events when reading file. Currently happens on HTML card generation.

## License

Released under GPL version 3.0 - see LICENSE and gpl-3.0.txt
