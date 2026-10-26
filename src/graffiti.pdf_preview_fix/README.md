# graffiti.pdf_preview_fix

Upload PDF files that have no preview image, with interaktiv.basetiles before 17.0.1.

## The problem

interaktiv.basetiles makes a preview image of the first page of a PDF file (behavior "preview image").
Before version 17.0.1 the whole upload fails if that does not work, with the error "could not generate PDF Image".
This happens for a damaged file, a file with a password, some encrypted files, or when the program `gm` (GraphicsMagick) is missing on the server.
Such a file can not be saved at all, and the PDF check of `graffiti.pdfcheck` can not report on it.

Since 17.0.1 interaktiv.basetiles saves the file without preview image (commit f8f98233 there).

## What this package does

`overrides.zcml` replaces the upload utility of interaktiv.basetiles with a subclass that saves the file without preview image, as 17.0.1 does.
All other errors stay as they are.
The package has no profile: it works as soon as it is in the buildout, and is gone when it is removed.

## When to remove it

When the project uses interaktiv.basetiles 17.0.1 or newer, or a 10.x version with the fix.
For newer versions the package changes nothing.

In Graffiti it is in the buildout of `main` (Plone 5.2, interaktiv.basetiles 10.0.5).
The Plone 6 buildout does not have it, interaktiv.basetiles 29 has the fix.

## Tests

```shell
bin/test -s graffiti.pdf_preview_fix
```
