# PDF check on upload

Version 1.0 (20.10.2026), changes in [CHANGELOG.md](CHANGELOG.md)

When an editor uploads a PDF file, Plone checks whether the file can be processed later: whether it opens, has readable text, can be rebuilt page by page with metadata, and whether pdfunite can append a second PDF and qpdf finds no errors.
The upload is never rejected.
The editor gets a warning with the reason, users who may change the file see the result in its view, and a workflow can ask for it in a guard expression.
Hints tell the editor what a later processing loses, for example bookmarks or form fields, without making the file unsuitable.

The check covers the content type File of Plone, and other content types that keep the PDF file in a field named `file`.
The checks run in their own process with a time and a memory limit, so a crafted or very large file can not block or crash the instance.
Projects add their own checks or hand the check to an external service without changing the package.

Everything else lives with the package, with screenshots, settings, the API for workflows and the script that checks files uploaded before: [src/graffiti.pdfcheck/README.md](../../../src/graffiti.pdfcheck/README.md).

## Requirements on the server

| Program | Package | Without it |
|---|---|---|
| pdfunite (Poppler) | `poppler-utils` | the step "append a second PDF" is skipped |
| qpdf | `qpdf` | the step "check the structure" is skipped |
| Python package `cryptography` | extra `graffiti.pdfcheck[crypto]` | files encrypted with AES get the finding `crypto_missing` |

pypdf is pinned in the buildout: 5.9.0 for Plone 5.2 (the last version for Python 3.8), for Plone 6 version 6.13 or newer.

## Installation in Graffiti

`graffiti.policy` installs the package, upgrade step 0013 installs it on existing sites.
Files that were uploaded before are checked with `scripts/check_pdf_files.py`.

`interaktiv.basetiles` before 17.0.1 stops the whole upload when it can not make a preview image of a PDF file, for example of a damaged file or of a file with a password.
Then the file is not saved and the PDF check can not report on it.
On `main` (Plone 5.2, `interaktiv.basetiles` 10.0.5) the buildout therefore has the package `graffiti.pdf_preview_fix`: it saves such files without a preview image, as 17.0.1 does (README in `src/graffiti.pdf_preview_fix` on `main`).
The Plone 6 buildout does not need it, `interaktiv.basetiles` 29 has the fix.

## Try it

`scripts/setup_demo_pdf_check.py` creates the folder `/pdf-check-examples` with one sample file for each finding and hint.
The files are made in code, the same samples as in the tests of the package, so no real document is needed.

```shell
bin/instance run scripts/setup_demo_pdf_check.py <site_id>
```

The script installs `graffiti.pdfcheck` in the site if needed, deletes `/pdf-check-examples` and creates it again.
Without an argument the site id is `site`.
It prints the result of each file and publishes nothing, visitors would not see the result anyway.

Log in and open the files: the view of each file shows the result, its description says what is special about it.
Without `graffiti.pdf_preview_fix` and with `interaktiv.basetiles` before 17.0.1, the upload of a damaged file, of a file with a password and of some encrypted files fails, see above.
The script then skips these files and says so.
