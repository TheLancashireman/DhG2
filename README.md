# DhG2
## Dave's genealogy assistant v2.0

This is a rewrite of the original, using python instead of perl and cleaning up a lot of the
cruft caused by major concept and design changes over the years.

At the moment the program is very much under development. Adding and editing card files is supported,
as is the analysis of relationships and display of trees.

There is a limited GEDCOM import feature that works for a very specific GEDCOM file created by FTM.
You have to import into an empty database, and there is no way to save the results as individual cards.

HTML generation is partially implemented:
* Descendant trees should be working for individuals; lists not supported yet.
* Card files can be generated but there are no events, transcripts or source file lists.
* Ancestor trees, name index etc. still to do.
* Publicity of people is not implemented - HTML generates everyone, even when private

Released under GPL version 3.0 - see LICENSE and gpl-3.0.txt

The program is unashamedly command-line driven. It doesn't give you a pretty interface to a hidden database.
Instead, it helps you to create structured text files, one per person, then analyses the files to produce ancestor
and descendant trees and immediate family reports. It can even produce a static HTML web site.

The text file approach means that you always have full control of your data

# To do

There is always lots to do. :-)
