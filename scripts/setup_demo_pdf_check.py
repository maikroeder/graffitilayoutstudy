""" Create the demo folder "PDF check examples" with one sample file for each finding and hint of graffiti.pdfcheck.

The files are made in code, the same samples as in the tests of the package, so no real document is needed.
Their description says what is special about them. Logged in, the view of each file shows the result of the check.
The script publishes nothing: visitors would not see the result anyway.

Usage:
    bin/instance run scripts/setup_demo_pdf_check.py [site_id]

The script is idempotent: the files in the folder are removed and created again, the folder stays.
"""
import sys

import plone.api as api
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
try:
    from plone.base.utils import get_installer  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.utils import get_installer
from graffiti.pdfcheck import api as pdfcheck
from graffiti.pdfcheck.settings import get_settings
from graffiti.pdfcheck.tests import samples
from plone.namedfile.file import NamedBlobFile
from zope.component.hooks import setSite
from zope.globalrequest import setRequest

SITE_ID = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith('.py') else 'site'
FOLDER_ID = 'pdf-check-examples'

# name of the sample, title, description; the results differ a little between the versions of pypdf
FILES = [
    ('good', 'Suitable file',
     'Two pages with text. The check finds nothing, so the view of the file shows no box.'),
    ('features', 'Form with a signature',
     'A bookmark, a form field, a signature and an embedded file. A later processing loses them: '
     'the view shows a note, the file stays suitable.'),
    ('damaged', 'Damaged file',
     'The file ends in the middle. No program can open it.'),
    ('password', 'File with a password',
     'The file only opens with a password, so no check can read it.'),
    ('edit_protection', 'Edit protection',
     'The file opens without a password, but it must not be changed. pdfunite can not append a second file.'),
    ('aes', 'Edit protection with AES',
     'Like "Edit protection", but encrypted with AES. Without the Python package cryptography '
     'the check can not read the text.'),
    ('no_text', 'No text, like a scan',
     'One page without text. A later processing finds no text in the file.'),
    ('broken_xref', 'Broken cross reference table',
     'The address of the table that lists the objects of the file is missing. pypdf 5.9 (Plone 5.2) reports '
     'the file as damaged, pypdf 6.13 and newer repair it. qpdf repairs it with a warning.'),
    ('rewrite', 'Page that can not be copied',
     'The page refers to an object that refers to itself. Rebuilding the file page by page fails.'),
    ('nested', 'Deeply nested object',
     'Copying the page makes Python 3.8 crash. The check runs in a process of its own, so Plone keeps running.'),
    ('pdfunite', 'Page that pdfunite leaves out',
     'The file says it has 0 pages. pdfunite leaves the page out without an error.'),
    ('not_pdf', 'Not a PDF file',
     'A text file with the extension .pdf. It is not checked, the view shows no box.'),
]

app = makerequest(app)  # noqa: F821 - provided by "bin/instance run"
setRequest(app.REQUEST)
admin = app.acl_users.getUser('admin')
newSecurityManager(None, admin.__of__(app.acl_users))

portal = app[SITE_ID]
setSite(portal)

installer = get_installer(portal, app.REQUEST)
if not installer.is_product_installed('graffiti.pdfcheck'):
    installer.install_product('graffiti.pdfcheck')
    print('installed graffiti.pdfcheck')
settings = get_settings()
if not settings['enabled'] or 'File' not in settings['portal_types']:
    print('note: the PDF check is switched off or does not check the content type File, the files get no result')

# the folder stays and keeps its UID, so that the link of the topic page "pdf-check"
# (scripts/setup_demo_topic_pages.py) keeps working; only the files in it are made again
if FOLDER_ID in portal:
    folder = portal[FOLDER_ID]
    api.content.delete(objects=list(folder.objectValues()), check_linkintegrity=False)
else:
    folder = api.content.create(container=portal, type='Folder', id=FOLDER_ID, title='PDF check examples')
folder.setDescription('Sample files for the PDF check, made in code. '
                      'The view of each file shows the result of the check.')
# out of the main menu, the topic page leads editors here; only these indexes, a full reindex would set the
# modification date to now
folder.exclude_from_nav = True
folder.reindexObject(idxs=['exclude_from_nav', 'Description'])

for name, title, description in FILES:
    filename = name.replace('_', '-') + '.pdf'
    savepoint = transaction.savepoint()
    try:
        # the check runs on adding, as with an upload
        obj = api.content.create(container=folder, type='File', id=filename, title=title, description=description,
                                 file=NamedBlobFile(data=samples.SAMPLES[name](), filename=filename))
    except Exception as error:  # noqa - interaktiv.basetiles before 17.0.1 fails on the preview image of some files
        savepoint.rollback()
        print('%s: not created, %s: %s' % (filename, type(error).__name__, error))
        continue
    result = pdfcheck.get_result(obj)
    if result is None:
        print('%s: no result' % filename)
    else:
        print('%s: %s' % (filename, ', '.join(result['findings'] + result['hints']) or 'suitable'))

transaction.commit()
print('created', folder.absolute_url())
