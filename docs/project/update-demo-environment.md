# Updating the demo environment graffiti.stage.interaktiv.de

This page only concerns the demo environment of Interaktiv GmbH.
It shows you how to roll out a new state there.

The GitLab pipeline only runs the tests, its deploy job is switched off because it no longer matched the server.
Updates go over SSH, on both hosts in the folder `graffiti`:

```shell
git fetch origin && git checkout <branch>
bin/buildout -c stage-plone.cfg     # Plone host; on the ZEO host: stage-zeo.cfg
bin/supervisorctl restart all
```

Scripts run with `bin/instance run` only work on the Plone host while the instance is stopped (`bin/supervisorctl stop instance`), otherwise the ZEO client cache is locked.

ZEO and Solr bind to `localhost` only (`buildout.d/zeo.cfg`, `buildout.d/zeo/solr.cfg`), neither has authentication.
They are reachable exclusively through the SSH tunnel, see [server-installation.md](server-installation.md), section 4.
Plone binds to `127.0.0.1:15001` only (`buildout.d/plone.cfg`), from outside it is reachable only through Apache.
To check after a restart: `ss -ltn | grep 15001` on the Plone host must show `127.0.0.1:15001`, not `0.0.0.0:15001`.

Extra programs next to Plone (for example a prototype) run under the same supervisor as files in `etc/supervisor.d/`, see [server-installation.md](server-installation.md), section 6.
They need no buildout run, only `bin/supervisorctl reread` and `bin/supervisorctl update`.

After the update, check that CSS and JavaScript of the tiles are built: `python3 scripts/check_tiles_assets.py`, background in [assets-and-styleguide.md](assets-and-styleguide.md).

The demo content is created by five scripts, all run on the Plone host with a stopped instance, in this order:

1. `scripts/setup_demo_entry_page.py` builds the entry page for authors.
2. `scripts/setup_demo_pdf_check.py` creates the folder with sample files for the PDF check, only editors see it.
3. `scripts/setup_demo_topic_pages.py` builds the topic pages of the main menu: working copies, exact search, PDF check, WebMirror and AI access (MCP).
   They link into the folders of the first two scripts. The entry page script creates its folder again on every run, so run the topic pages after it.
4. `scripts/setup_demo_front_page.py` rebuilds the front page with a card per topic page and refreshes the WebMirror example.
5. `scripts/setup_demo_theme.py` sets the look: values of the tiles styleguide, the footer, the header images of the main pages, the logo and the favicon.
   It runs Grunt afterwards, so `style.css` is rebuilt.
   Background in [src/graffiti.theme/README.md](../../src/graffiti.theme/README.md).

All of them can run again at any time, the result is the same.

The topic pages and the entry page share one layout from `scripts/demo_common.py`: a lead text with a card "At a glance", numbered steps under "Try it", the feature itself, "How it works" with links to the documentation.
The example documents of the entry page get dates of the last hours and days, the demo pages a date five days back, so that lists of recently changed content start with the examples.
The exact search has a tiles page with a search field as default page of `suche-demo` now. The earlier hint page `suche-demo/such-seite` stays out of the menu and can be deleted by hand.
