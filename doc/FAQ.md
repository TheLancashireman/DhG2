# Frequently-asked questions

The "frequently-asked" part might not be entirely true.  :-)

## Why did you write DhG2?

See the blog post [Family snapshot](https://thelancashireman.org/blog/2024/2024-11-27-dhg2.html).

## Why do I get a message 'Unrecognised header line: "sex" ignored ...'?

This usually happens when you use the **new** command to create a person. If DhG2 cannot
determine the gender from the name, the default template places the word "sex" there instead.

You can edit the person's file and set the gender to *Male*, *Female* or *Unk* as appropriate.
If you don't, you'll get the message for every file whenever you start DhG2 or reload the
database.

DhG2 builds up a list of name-to-gender mappings when it loads the database, so as your database
grows, the likelihood of getting this message gets less as time goes on.

## Yes, but why don't you just use "Unk" by default?

Using an unrecognised value means you get the message as a reminder to edit the file.

If you don't want to use the gender information at all, you could create a custom template for
new cards. See [advanced topics](Advanced.md) for more information.

## What is DhG_Specials.py?

This file contains some extensions to DhG_Shell.py that perform special operations in the
author's database. The operations depend on the conventions used by the author; for example,
that England and Wales census records have a Source of the form "Census record HO107..." or
"Census record RG...". If you don't follow this convention, the features won't be very useful.

To use DhG_Specials.py, just invoke it instead of DhG_Shell.py. Apart from the extra commands,
it behaves in an identical manner. Note: the author only uses DhG_Specials.py when the extra
features are needed, and usually in a non-interactive script.

There is no documentation for the special features apart from the built-in help.
