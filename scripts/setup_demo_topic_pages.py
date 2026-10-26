""" Build the topic pages of the demo site: one page per feature in the main menu.

Usage:
    bin/instance run scripts/setup_demo_topic_pages.py [site_id]

Every topic page has the same parts (demo_common.topic_rows): a lead text with a card "At a glance",
"Try it" with numbered steps, the feature itself where visitors can use it, "How it works" and a card with
links to the documentation. The steps are also the test plan for us. Visitors only look, steps that need
a login are marked.

- Working copies: a tiles page "working-copies" with screenshots of the documentation. The script turns on
  the working copy behavior for "Page", so signed-in editors can try it.
- Exact search: a tiles page "exact-search" with a search field as default page of the folder "suche-demo"
  (the folder and its test pages were made by hand on the demo site).
- PDF check: a tiles page "pdf-check" with screenshots of the documentation. It links to the example files of
  scripts/setup_demo_pdf_check.py, which only editors see.
- WebMirror: a tiles page "static-websites" that leads to the example "testmirror1".
- AI access (MCP): a tiles page "about-mcp" as default page of the folder "mcp-demo", if the folder exists
  (its documents come from the MCP server branch).
- Entry pages: scripts/setup_demo_entry_page.py builds that page itself.

Run it after setup_demo_entry_page.py and setup_demo_pdf_check.py (the pages link into their folders; the entry page
script creates its folder again on every run), then setup_demo_front_page.py (its cards link to these pages) and
setup_demo_theme.py (it sets the header images of these pages). Running the script twice gives the same result.
"""
import os
import sys

import interaktiv.framework as framework

# "bin/instance run" puts its own options in front of the script name, the arguments follow it
SCRIPT_ARGS = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
SCRIPT_ARGS = SCRIPT_ARGS[max(i for i, arg in enumerate(SCRIPT_ARGS) if arg.endswith('.py')) + 1:]
SITE_ID = SCRIPT_ARGS[0] if SCRIPT_ARGS else 'site'
SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
SCRIPTS = os.path.dirname(os.path.abspath(SCRIPT_PATH))
REPO = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import demo_common  # noqa: E402 - needs the folder of the scripts on the path
from demo_common import DOCS, REPO_URL, card, doc_link, row, text_tile  # noqa: E402

# the MCP server is not merged yet, its documentation lives on its branch
MCP_DOCS = REPO_URL + '/-/blob/22842-mcp_server/mcp-server/README.md'
MCP_URL = 'https://graffiti.stage.interaktiv.de/mcp'
WORKINGCOPY_BEHAVIOR = 'interaktiv.workingcopy.behaviors.workingcopy.IWorkingcopyBehavior'
# screenshots of the documentation of the packages: prefix of the image ids, folder
SCREENSHOTS = {
    'workingcopy': os.path.join(REPO, 'src', 'interaktiv.workingcopy', 'docs'),
    'pdfcheck': os.path.join(REPO, 'src', 'graffiti.pdfcheck', 'docs'),
}
PLONE_VERSIONS = 'Plone 5.2 and 6.1'
# order of the main menu
MENU = ['entry-authors', 'working-copies', 'suche-demo', 'pdf-check', 'static-websites', 'mcp-demo']

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"
link = lambda path, text: demo_common.link(portal, path, text)  # noqa: E731


def screenshot(file_name, alt, crop=None, package='workingcopy'):
    """ A screenshot of the documentation, or the part of it that fits into a card, linked to the image """
    image = demo_common.upload_image(portal, os.path.join(SCREENSHOTS[package], file_name),
                                     package + '-' + file_name[:-len('.png')], 'Screenshot: ' + alt, crop=crop)
    uid = image.UID()
    return (f'<p class="graffiti-screenshot"><a href="resolveuid/{uid}/@@images/image">'
            f'<img src="resolveuid/{uid}/@@images/image/large" alt="{alt}"></a></p>')


def build(page, **parts):
    demo_common.rebuild_tile_page(page, demo_common.topic_rows(**parts))
    # pages of the demo itself, not content of the example intranet
    demo_common.date_back(page)
    print('topic page:', page.absolute_url())


# Working copies
framework.storage.set_behavior(behavior=WORKINGCOPY_BEHAVIOR, portal_types=['Document'])
build(
    demo_common.get_or_create_tile_page(
        portal, 'working-copies', 'Working copies',
        'Change a published page in a copy and publish the changes in one step.'),
    lead=(
        '<p class="lead">Editors often need to change a page that is already online. With a working copy they '
        'change a copy, while readers still see the original.</p>'
        '<p>When the copy is ready, they compare both versions and publish the changes in one step. '
        'Nothing half-finished shows up on the site.</p>'
    ),
    facts=[
        ('For', 'Editors'),
        ('Login', 'Needed. The screenshots show every step.'),
        ('Package', 'interaktiv.workingcopy'),
        ('Runs on', PLONE_VERSIONS),
    ],
    try_intro='<p>Signed in as an editor, open a page, for example '
              + link('entry-authors/document-maintenance-policy', 'Policy for maintaining documents') + '.</p>',
    steps=[
        ('Create a working copy',
         '<p>Choose <em>Actions</em> and then <em>Arbeitskopie erstellen</em> (create a working copy). '
         'The labels are German for now.</p>'
         + screenshot('actions-menu.png', 'The menu Actions with the entry for a working copy')),
        ('Change and compare',
         '<p>Change the copy. A bar links the copy and the original. Compare both: removed text is red, '
         'added text is green.</p>'
         + screenshot('compare.png', 'Comparison of the working copy with the original', crop=(0, 0, 430, 310))),
        ('Publish the changes',
         '<p>Check the copy in: it replaces the original in one step. Or cancel it, then nothing changes.</p>'
         + screenshot('check-in.png', 'The form for checking in a working copy', crop=(0, 0, 430, 367))),
    ],
    how=(
        '<p>The package interaktiv.workingcopy builds on plone.app.iterate, the working copies that come with Plone. '
        'It differs in three points: it is turned on per content type as a behavior, on this site for pages. '
        'It needs no versioning of the content type. And it unlocks the original when a copy is deleted.</p>'
        '<p>The comparison uses the diff tool of Plone, field by field. Events after checking out, checking in and '
        'cancelling let other packages react.</p>'
    ),
    docs=[
        (DOCS + 'src/interaktiv.workingcopy/README.md', 'interaktiv.workingcopy, step by step with screenshots'),
        ('https://github.com/plone/plone.app.iterate', 'plone.app.iterate'),
    ],
)

# Exact search: the folder and its two test pages exist on the demo site
if 'suche-demo' in portal:
    folder = portal['suche-demo']
    folder.setTitle('Exact search')
    folder.setDescription('A search for the title of a document finds this document first.')
    for test_page_id, test_page_title in [
        ('ich-bin-ein-test', 'I am a test'),
        ('voellig-irrelevanter-inhalt', 'Totally irrelevant title'),
    ]:
        if test_page_id in folder:
            folder[test_page_id].setTitle(test_page_title)
            folder[test_page_id].reindexObject(idxs=['Title', 'sortable_title', 'SearchableText'])
    # the earlier hint page, a plain page without room for a search field, stays out of the menu
    if 'such-seite' in folder:
        folder['such-seite'].exclude_from_nav = True
        folder['such-seite'].reindexObject(idxs=['exclude_from_nav'])
    page = demo_common.get_or_create_tile_page(folder, 'exact-search', folder.Title(), folder.Description())
    folder.setDefaultPage('exact-search')
    folder.reindexObject(idxs=['Title', 'Description', 'sortable_title', 'SearchableText'])
    demo_common.block_portlets(folder)
    build(
        page,
        lead=(
            '<p class="lead">A search for the title of a document should find this document first.</p>'
            '<p>The usual search splits the words, so a page that repeats one of them many times can come first '
            'instead. Graffiti adds an exact search with Solr: a search for a complete title puts that page at '
            'the top.</p>'
        ),
        facts=[
            ('For', 'Everyone who searches'),
            ('Login', 'Not needed'),
            ('Package', 'graffiti.search, with Solr and collective.solr'),
            ('Runs on', PLONE_VERSIONS),
        ],
        steps=[
            ('Search for a title',
             '<p>Type <strong>I am a test</strong> into the search field below and press Enter. The suggestions '
             'that show up while you type use the usual search for now.</p>'),
            ('Look at the order',
             '<p>On the search page, ' + link('suche-demo/ich-bin-ein-test', 'I am a test') + ' comes first, although the '
             'page ' + link('suche-demo/voellig-irrelevanter-inhalt', 'Totally irrelevant title')
             + ' contains the word "test" dozens of times.</p>'),
        ],
        extra_rows=[
            row(('TileSearch', {'title': 'Search', **demo_common.card_values(color='graffiti-sky')})),
        ],
        how=(
            '<p>A small patch of collective.solr adds the placeholder <code>{raw_value}</code> to the search '
            'pattern: the search text as typed, not split into words. The Solr schema copies the title into two '
            'fields that match the whole title or its start. The search pattern itself is set in the Solr '
            'control panel.</p>'
        ),
        docs=[
            (DOCS + 'docs/features/exact-search/README.md', 'Exact search'),
            (DOCS + 'src/graffiti.search/README.md', 'graffiti.search'),
        ],
    )
    demo_common.date_back(folder)

# PDF check: the example files are in the folder of scripts/setup_demo_pdf_check.py, only editors see them
build(
    demo_common.get_or_create_tile_page(
        portal, 'pdf-check', 'PDF check',
        'Checks PDF files on upload whether they can be processed later.'),
    lead=(
        '<p class="lead">Documents in an intranet are often processed later: rebuilt page by page, given new '
        'metadata or put together with a second PDF file. Some files do not survive that.</p>'
        '<p>The PDF check finds such files when they are uploaded. The upload is never rejected: the file is saved, '
        'the editor gets a message when something is found, and the result is stored at the file, so that a '
        'workflow can ask for it.</p>'
    ),
    facts=[
        ('For', 'Editors who upload PDF files'),
        ('Login', 'Needed. The screenshots show every step.'),
        ('Package', 'graffiti.pdfcheck, with pypdf, pdfunite (Poppler) and qpdf'),
        ('Runs on', PLONE_VERSIONS),
    ],
    try_intro='<p>Signed in as an editor, upload a PDF file into a folder. Example files for every finding are in '
              + link('pdf-check-examples', 'PDF check examples') + ', for editors only.</p>',
    steps=[
        ('Upload a PDF file',
         '<p>Right after the upload a message says when the file can probably not be processed later, a suitable '
         'file gets no message. The view of the file shows the findings to everyone who may change it.</p>'
         + screenshot('upload-findings.png', 'The findings of the PDF check in the view of a file',
                      crop=(130, 640, 600, 810), package='pdfcheck')),
        ('Read the hints',
         '<p>Hints do not make a file unsuitable. They say what a later processing loses, for example bookmarks or '
         'form fields. The technical details list what the programs found.</p>'
         + screenshot('upload-hints.png', 'Hints of the PDF check with the technical details',
                      crop=(130, 455, 600, 600), package='pdfcheck')),
        ('Choose the checks',
         '<p>In the settings of the PDF check, administrators switch it on or off and choose the checks, the '
         'content types and the limits for time, memory and the size of a file.</p>'
         + screenshot('settings.png', 'The settings of the PDF check', crop=(0, 50, 560, 600), package='pdfcheck')),
    ],
    how=(
        '<p>While the file is saved, the check runs in a process of its own, with limits for time and memory, and '
        'the upload waits for it. It opens the file and reads its text with pypdf, rebuilds it page by page with new '
        'metadata, appends a blank page with pdfunite and checks its inner structure with qpdf.</p>'
        '<p>The result stays at the file as long as the file stays the same. An incomplete check, for example after '
        'a timeout, runs again the next time the file is saved. Files that are no PDF stay untouched, files larger '
        'than the limit get a hint.</p>'
    ),
    docs=[
        (DOCS + 'docs/features/pdf-check/README.md', 'PDF check'),
        (DOCS + 'src/graffiti.pdfcheck/README.md', 'graffiti.pdfcheck'),
    ],
)

# WebMirror
build(
    demo_common.get_or_create_tile_page(
        portal, 'static-websites', 'WebMirror',
        'A small static website as a ZIP file, shown inside the Plone layout.'),
    lead=(
        '<p class="lead">Some content already exists as a small static website, for example a handbook exported '
        'from another tool.</p>'
        '<p>A WebMirror holds such a website as a ZIP file and shows its pages inside the Plone layout, at the '
        'address of the object. To change the pages, editors upload a new ZIP file. No deployment is needed.</p>'
    ),
    facts=[
        ('For', 'Editors and readers'),
        ('Login', 'Not needed to look, needed to upload'),
        ('Package', 'graffiti.contenttypes, content type WebMirror'),
        ('Runs on', PLONE_VERSIONS),
    ],
    steps=[
        ('Open the handbook',
         '<p>Open the example ' + link('testmirror1', 'Author handbook') + '. Its pages come from a ZIP file, '
         'the frame around them is Plone.</p>'),
        ('Browse its pages',
         '<p>Use the navigation of the handbook: Overview, Workflow, Checklist. The addresses stay below the '
         'WebMirror, for example <code>…/workflow.html</code>.</p>'),
        ('Upload a new version',
         '<p>Signed in, editors add a WebMirror to a folder and upload a ZIP file with an '
         '<code>index.html</code>. A new ZIP file replaces all pages at once.</p>'),
    ],
    extra_rows=[
        row(
            card('Inside the ZIP file',
                 '<h3>Inside the ZIP file</h3>'
                 '<pre>index.html\nworkflow.html\nchecklist.html\nimages/\n    checklist.svg\n    workflow.svg</pre>',
                 color='graffiti-sky', gridsize=5),
            text_tile('The example',
                      '<h3>The example</h3>'
                      '<p>The ZIP file of the example has three pages and two images. Plone shows the body of each '
                      'page and rewrites its links and image paths, so the pages link to each other below the '
                      'WebMirror.</p>'
                      '<p>The ZIP file is part of the repository: ' + doc_link(
                          'docs/examples/WebMirror_example.zip', 'WebMirror_example.zip') + '.</p>',
                      gridsize=7),
        ),
    ],
    how=(
        '<p>The ZIP file is stored in Plone. Every Plone host unpacks it into a local cache, so several hosts serve '
        'the pages from their own disk. Plone shows the body of each HTML page in its layout and rewrites links and '
        'image paths. Stylesheets and scripts of the website are not loaded.</p>'
    ),
    docs=[
        (DOCS + 'docs/features/webmirror/README.md', 'WebMirror'),
    ],
)

# AI access (MCP)
if 'mcp-demo' in portal:
    folder = portal['mcp-demo']
    folder.setTitle('AI access (MCP)')
    folder.reindexObject(idxs=['Title', 'sortable_title', 'SearchableText'])
    page = demo_common.get_or_create_tile_page(
        folder, 'about-mcp', 'AI access (MCP)',
        'AI assistants search the documents of this site and read their PDF files.')
    folder.setDefaultPage('about-mcp')
    demo_common.block_portlets(folder)
    build(
        page,
        lead=(
            '<p class="lead">AI assistants can answer questions with the documents of an intranet, if they may '
            'search them.</p>'
            '<p>The Model Context Protocol (MCP) is an open standard for this. Graffiti runs an MCP server next to '
            'Plone: an assistant searches the published documents of this site and reads their PDF files.</p>'
        ),
        facts=[
            ('For', 'AI assistants and the people who use them'),
            ('Login', 'Not needed, the server runs in a test mode for a limited time'),
            ('Software', 'A separate MCP server that talks to plone.restapi'),
            ('Status', 'Test version, not merged yet'),
        ],
        try_intro=(
            '<p>Add the server to an MCP client, for example Claude Code:</p>'
            f'<pre>claude mcp add --transport http graffiti {MCP_URL}</pre>'
            f'<p>Other clients take the address <code>{MCP_URL}</code> with the transport "Streamable HTTP", '
            'for example the MCP Inspector (<code>npx @modelcontextprotocol/inspector</code>). Then ask:</p>'
        ),
        steps=[
            ('Search', '<p>"Search for travel in the MCP demo documents."</p>'),
            ('Read a PDF file', '<p>"Download the travel expense guidelines."</p>'),
            ('See the limits',
             '<p>"Download the annual report." It is larger than 3 MB, so the server only gives the address.</p>'),
        ],
        extra_rows=[
            row(
                text_tile('The test documents',
                          '<h3>The test documents</h3>'
                          '<p>PDF files, a large scanned report and a page without a PDF. A draft in a private '
                          'subfolder stays invisible to the server.</p>',
                          gridsize=4),
                ('TileListing', {'title': 'Documents', 'gridsize': 8}),
            ),
        ],
        how=(
            '<p>The server is a separate Python process. It talks to Plone only through plone.restapi, as a visitor '
            'without login, so it only finds what visitors may see. It offers two tools, <code>search</code> and '
            '<code>download</code>, and reads PDF files up to 3 MB. It never changes anything in Plone. Limits per '
            'client protect the site, and every request is logged.</p>'
        ),
        docs=[
            (MCP_DOCS, 'MCP server (not merged yet)'),
            ('https://modelcontextprotocol.io', 'Model Context Protocol'),
        ],
    )
    demo_common.date_back(folder)

# main menu: the topic pages in this order, before everything else
for position, obj_id in enumerate(MENU):
    if obj_id in portal:
        obj = portal[obj_id]
        if getattr(obj, 'exclude_from_nav', False):
            obj.exclude_from_nav = False
        demo_common.publish(obj)
        portal.moveObjectToPosition(obj_id, position)
        obj.reindexObject(idxs=['exclude_from_nav', 'getObjPositionInParent', 'review_state'])
portal.plone_utils.reindexOnReorder(portal)
print('menu:', [obj_id for obj_id in MENU if obj_id in portal])

demo_common.commit()
