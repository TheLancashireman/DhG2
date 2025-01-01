# Advanced topics

## Generating a website

The website that DhG2 generates has four parts:

* A set of pages for individuals, one for each person.
* An index to the individuals' pages.
* A set of trees showing the descendants of selected persons.
* A set of trees (Ahnentafel) showing the ancestors of selected persons.

In addition, you need a top-level page that provides a starting point.

You can find examples of these page types on ther author's website:

* An [HTML page for an individual](https://thelancashireman.org/family-history/cards/Haworth/JohnHaworth-396.html)
* The [index to the whole site](https://thelancashireman.org/family-history/surname-index.html)
* A [tree of descendants](https://thelancashireman.org/family-history/trees/JohnHaworth-377-descendants.html)
* An [Ahnentafel](https://thelancashireman.org/family-history/trees/JohnHaworth-396-ancestors.html)

The **htmldescendants** and **htmlancestors** commands accept as parameters files containing lists
of the individuals' trees that you want to generate.

### Public or private?

Before you go about generating a website, you should decide what you want to include in it. Your family
database is likely to contain living or recently-deceased relatives and the information about them might
be personal and sensitive.

Is the website going to be published on the internet for all to see? If so, you probably don't want to
publish all of your database. It is certainly recommended to omit individuals who are still alive.
However, living individuals will still appear as links from deceased individuals individuals.

DhG2 has a simple way to determine, automatically, which persons should appear on a public website.
A person is considered to be explicitly "private" if they have no death record or if they are explicitly
marked as "Private". In addition to this, DhG2 considers as "private" all persons who are descendants,
siblings, spouses or siblings of spouses of a person who is explicitly "private".

### Individuals' HTML pages and the index

The **htmlcard** command has a parameter that generates HTML pages for all individuals in the database except
for those individuals that are detemined to be private.

The **htmlindex** command has a parameter to generate an index that contains all individuals in the database except
for those individuals that are detemined to be private.

### Family trees

The **htmlancestors** trees are not a problem because you explicitly tell it whose trees to generate. The
assumption is that you do not generate ancestor trees for individuals that are private.

In the desecndants trees, the generation needs to stop whenever a private individual is found. The
**generate** configuration variable controls this; if you set **generate** to *public*, generation
of the level stops when a private individual is encountered. The entire set of children is replaced
with a link to a generic page that you can write to explain the privacy policy.

The same parameter inhibits the generation of a list of children on an individual's HTML page, if one
of the children is private.

### Summary

To generate a website for deployment on a public server:

* Set the "generate" variable to *public*
* Run **htmlcard @public**
* Run **htmlindex @public**
* Create a list of people whose ancestor trees you want.
* Run **htmlancestors** &#64;*FILENAME* using the list of ancestor trees.
* Create a list of people whose descendant trees you want.
* Run **htmldescendants** &#64;*FILENAME* using the list of descendant trees.

To generate a website for deployment on a private server that is not visible on the internet:

* Set the "generate" variable to *all*
* Run **htmlcard @all**
* Run **htmlindex @all**
* Create a list of people whose ancestor trees you want. This will differ from the list for a public website.
* Run **htmlancestors** &#64;*FILENAME* using the list of ancestor trees.
* Create a list of people whose descendant trees you want. This is likely to be the same list as for a public website.
* Run **htmldescendants** &#64;*FILENAME* using the list of descendant trees.

If you use the default templates for HTML your website will need a CSS style sheet called
"/styles/family-history.css". You can [obtain this file](https://thelancashireman.org/styles/family-history.css)
from the author's website and modify it as you wish.

## Adapting templates

Most of the information that DhG2 displays and all of the generated files are controlled by templates.

There's a standard set of templates that is probably suitable for most interactive work, but for
generating a web site you will almost certainly want to adapt the header and footer templates for HTML.

This section gives a short introduction to the templates but a detailed explanation of the Jinja2
template language and HTML/CSS is beyond the scope of this document.

### Creating a custom template

You do not need to modify the installed copy of DhG2 in order to use a customised template. DhG2
searches a list of locations specified in the **tmpl_path** variable for all templates. All you
need to do is to ensure that a template of the same name appears earlier in the list of locations.

If you use the default value of the **tmpl_path** variable, DhG2 first looks in `~/.DhG/templates`
so any template files in that directory will override the installed templates.

As an example of how to create a custom template we will modify what DhG2 puts into a new person's
card file to eliminate the ""sex" error message that's mentioned in the [FAQ](FAQ.md).

* Copy the `new-person-card.tmpl` file from the DhG2 installation directory to `~/.DhG/templates`.
* Edit `~/.DhG/templates/new-person-card.tmpl` with a standard text editor.
* Change the word "sex" to "Unk".
* Save the file and close the editor.

From now on, every person that you add to the database will have "Unk" (unknown) as their gender.

To undo your adaptation, simply delete the new template or rename it to something else that DhG2 doesn't
look for.

### The template dictionary

DhG2 provides each template with a dictionary called **tp** that the template can access to
obtain values to place into the generated file. You can see this in the new card template:
`tp['name']`, `tp['uniq']` etc. are used in the template.

The content of the dictionary varies from template to template. However, every template gets the
following information:

* tp['config'] contains a reference to the configuration class so that the template can access configuration variables.
* tp['timestamp'] contains the time of generation in UTC as a string.
* tp['tmpl_name'] contains the name of the template to be used. For non-HTML templates it's just the template file name.
   
### Adapting the HTML templates

Adapting the main HTML templates would be a fairly complex task that might even require modifications to the
Python code of DhG2. However, it's fairly straightforward to change the style of the web pages by
changing just the wrapper template (`html-wrapper.tmpl`). This file is used as the outer template for
all HTML files. It includes another template to generate the main content of the page. The name of
the included template is passed in tp['tmpl_name'].

As for the new card example above, copy the `html-wrapper.tmpl` file from the DhG2
installation to your personal template location, then edit them as necessary. The wrapper
file that generates the author's website are provided for reference. The reference file includes
various small javascript snippets that you can obtain from the author's site. For example, the
`collapsible.js` script used in the HTML index page expands and collapses the initials and surnames
lists when you click on them. Without this script, the entire index is visible all the time.
