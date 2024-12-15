# Structure of the card file

In DhG2, each person in the database is represented by a text file called a "card file". Think
of it as a card in a card index (rolodex or whatever) but with the advantage of having much more
space to store information. DhG2 accepts UTF-8 in the card files.

The way you write the information in the card file is important. DhG2 uses the keywords
to construct family trees and to produce the HTML files for a website.

Apart from the ".card" suffix, the name of a card file is unimportant. DhG2 scans the entire
database directory for files with suffix ".card". However, if you use the "new" command,
DhG2 creates a file with a name constructed from the full name and unique number of the person and
places it in a subdirectory of the person's surname.

DhG2 ignores blank lines and lines that start with a '#' character. You can therefore use the
'#' character to add comment lines wherever you like.

In general, lines that start with a '|' character are considered to be continuation lines.
However, continuation lines are only processed for specific types of information.

## An example card file

Each card file is divided into three sections:
* Header information that identifies the person and provides general information.
* A list of events for the person, including birth and death events.
* Additional free-format information that DhG2 does not parse. This section is optional.

The header information starts at the beginning of the file and ends at the first line that has
either a numerical digit or a '?' as the first character. After that, all lines are considered
as part of an event until a line equalling "EOF" is found. The lines after EOF are not parsed.

The structure of a card file is best described by giving an example. The following file
describes a man called John Butson who lived from 1780 until 1833.
```text
Name:       John Butson
Uniq:       3463
Male
Father:     Peter Butson [595]
Mother:     Mary Bateman [3459]
Version:    2

1780-12-01~ Birth
+Source     Estimated from baptism record

1780-12-24  Baptism
+Place      St Mary and St Cuthbert, Chester-le-Street, County Durham
+Abode      Fatfield, Chester-le-Street, County Durham
+Source     Parish register (BT)
-File       Image       Chester-le-Street-Baptism-1780-BT-145.jpg
-Transcript
| Chester le Street Baptisms 1780
| December
| 24  John Son of Peter Butson of Fatfield Horsekeeper & Mary his Wife

1797-05-01  Marriage    Ann Maria Wheatley [3465]
+Place      St Mary and St Cuthbert, Chester-le-Street, County Durham
+Abode      Chester-le-Street, County Durham
+Witness    George Wheatley
+Witness    William Pybus
+Witness    Isabella Peacock
+Source     familysearch
-URL        https://www.familysearch.org/ark:/61903/1:1:NLZX-NJW
-Transcript
| John Batson & Ann Maria Wheatley  Marriage  1 May 1797  Chester le Street, Durham, England
+Source     durhamrecordsonline
-Transcript
| Marriages, Chester-le-Street District - Record Number: 191775.1
| Location: Chester-le-Street, County Durham
| Church: St. Mary and St. Cuthbert
| Denomination: Anglican
| 1 May 1797 John Batson (of this parish) married Maria Wheatley (of this parish), by banns
| Witnesses: George Wheatley; William Pybus; Isabella Peacock

1833-09-19~ Death
+Age        61
+Abode      Birtley, Chester-le-Street, County Durham
+Source     Estimated from burial record

1833-09-22  Burial
+Place      St Mary and St Cuthbert, Chester-le-Street, County Durham
+Source     Parish register (BT)
-File       Image       Chester-le-Street-Burial-1833-BT-1476.jpg
-Transcript
| Burials in the Parish of Chester-le-Street in the County of Durham in the year 1833
| 1052  John Butson  Birtley  Sept'r 22nd  61 years  John Dodd Sub Curate
```

Details about the sections and their content follows.

## The header section

The file header contains mandatory information about the person (name, unique number) along
with some optional information. Each line holds one piece of information. Most lines of the header
are of the form "Keyword:  Value", but there are some with no "value" part that are entered without the colon.

In the example, the person's name is John Butson. He is male and his unique numbver in the database is 3463.
His father was Peter Butson (uniqe number 595) and his mother was Mary Bateman (3459). This is the
mother's maiden name. The presence of unique numbers for father and mother imply that they both have
card files in the database.

The full set of header lines is described in the following sections. Lines with unrecognised keywords are
ignored with a warning message.

* Name: - This mandatory line is the name of the person as normally written. DhG splits this name into parts based
on space characters; the last part is considered to be the surname. In the example above,
Bloggs is the surname. If you have someone called Cordelia Ponsomby-Smyth, the surname is
Ponsomby-Smyth. However, in the case of Ludwig van Beethoven, "van" is considered to be a
forename.

* Uniq: - This mandatory line is the unique identifier for the person. Its value is a strictly positive
integer number.

* Male, Female, Unk - This mandatory line specifies the sex of the person.

*  Father: - This line is not strictly mandatory, but if you omit it, DhG2 cannot construct family trees. It
is therefore mandatory wherever it is known.
The value is either "Name [Unique number]" or just "Name". The unique number is used by DhG2 to construct
family trees. If only a name is provided, the name is used in some HTML pages but no lineage is inferred.

* Mother: - This line is not strictly mandatory, but if you omit it, DhG2 cannot construct family trees. It
is therefore mandatory wherever it is known.
The value is either "Name [Unique number]" or just "Name". The unique number is used by DhG2 to construct
family trees. If only a name is provided, the name is used in some HTML pages but no lineage is inferred.

* Private - This line has no value part; it is either present or absent. If present, it restricts the content of
public web pages.

* Version: - In principle, this line defines the structure version of the card file. DhG2 only supports version 2;
version 1 was the first attempt and is now obsolete. The Version line is retained for compatibility and might be
re-introduced in the future if the structure changes again.

* ToDo: - This line and any continuation lines are ignored by DhG2. You can use the keyword to remind you of research
that is still needed.

* Nickname: - You can use this to record a nickname that the person was known by.

* Alias: - You can use this to record another name by which the person was known.

* Occupation: - If the person kept the same occupation for most of their life, you might want to record it using
this keyword.  Continuation lines are processed.

* Photo: - You might use this keyword to introduce a photo of the person. However, the usage isn't defined yet.

* Source: - Gives information about the source of the information provided in the header.
Continuation lines are processed.

* Note: or Notes: - Additional free-format information. Continuation lines are accepted.

## The event section

A person's lifetime is described in a sequence of events, from birth to death and beyond in the case of
burial and probate records.

While it is possible to construct a family tree using only the header information, it is useful to
provide at least the birth and death events. If there is no birth event, DhG2 cannot determine
the order of children in a family. If there is no death event, DhG2 assumes that the person is still
alive, which restricts the generation of a public website.

Each event is introduced by an event line of the form
```text
DATE   EVENT
```
### Event date

DATE is given in YYY-MM-DD format if the exact date is known. YYYY-MM and YYYY are also valid dates.
These three forms can be suffixed with one of '~', '<', '>', meaning "about", "before" and "after",
respectively.
For events like entries in the UK birth, marriage and death indexes, where only the year and quarter is
known, YYYY-Qn is also accepted. "?" is also accepted as a date; it means the date is not known.

In the example, John Butson was baptised on 24th December 1780. Based on that information, his
date of birth is estimated as 1st December of the same year.

### Event text

With three exceptions, EVENT can be any text that describes the event. The exceptions are:

* Marriage - the rest of the line is the name and unique number of the spouse.
* Partnership - the rest of the line is the name and unique number of the partner.
* Misc - the rest of the line is treated as text that describes the event.

The Misc event is deprecated; it is retained for backward compatibility.

The event types Birth, Death, Marriage and Partnership are used by DhG2 to construct family trees. All other
event types are considered extra information about the person. They are placed in the timeline when creating
a website, but otherwise play no role.

In the example, John Butson was baptised at St Mary and St Cuthbert, Chester-le-Street. At the time
he was living in Fatfield.

His marriage took place at the same church on 1st May 1797. The witnesses were George Wheatley,
William Pybus and Isabella Peacock.

He was buried on 22nd September 1833, again at St Mary and St Cuthbert. His date of death is estimated
from the burial record. He was 61 years old at the time.

The lines following an event line must be prefixed with either '+', '-' or '|' as follows:

* '+' gives some primary information derived from the event, such as age, birthplace etc. 
* '-' gives some secondary information related to the primary information immediately preceding.
* '|' indicates a continuation line.

The word immediately following a '+' or '-' line (with no invervening space) is a keyword. The remainder of
the line is the value. You can choose the keywords freely. For example, you might use "+Abode" to give
the person's address at the time of the event, or "+Age" to give their age.

With a few exceptions, the keywords have no special meaning in DhG2. The exceptions are:

* "-URL" gives a URL related to the preceding "+" information. It causes a link to be generated in the website page.
* "-Uniq" gives the unique number of a person whose name is given in the preceding '+' information. This might be
a witness to a wedding, for example, when the witness is a family member.
* "+Source" indicates a source of the information in the event. This is described in detail below.

### Source information

Source information is handled differently to other event-related information when creating the web pages.
Sources are presented in a separate column in the timeline. Files and transcripts are placed in tables below the
timeline and links are provided in the source description.

Source information starts with a "+Source" keyword immediately followed (on the same line) with a description of the
source, such as "Parish register", "Census record" etc.

The lines following the "+Source" line that are understood by DhG2 are:

* "-File" gives the type and name of a file stored somewhere on your computer.
* "-URL" gives a link to where you can find the information on the internet.
* "-Transcript" gives a transcription of the source. The transcription is placed on continuation lines.

The text of a "-Transcript" is copied verbatim into the transcripts table in the web page. In addtition,
the content of files with type "Transcript" will be copied provided that the file suffix matches the suffix
specified in the configuration.

In the example, John Butson's marriage was found on the familysearch website. The URL is provided along
with a brief transcript. More detail was obtained from the Durham Records Online website. Deep linking
is not possible so only a transcript is provided.

John Butson's burial record came from the bishop's transcript of the parish register. The
filename of an image of the page is given, along with transcript of the page header and the line of the register.

## Text after the EOF line

The events end at the end of the file or at a line containing only "EOF".

DhG2 ignores anything after "EOF", so you can use it for recording information that you have gathered that
still needs to be pieced together. As an example, the author sometimes records a list of children here
temporarily, during the process of creating individual records for the children.

