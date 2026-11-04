# openheidelberg.layout

Page layouts for the OpenHeidelberg site on top of Plone's `main_template`: a Diazo theme with one theme file
per layout, and a behavior that lets a TilePage choose its layout.

Status: structure in place, checked offline with the Diazo compiler on a Plone-like test page (see "Checked");
not yet installed or run in Plone.

## Layouts

| Id | Used by | What it is |
|---|---|---|
| `site-search-layout` | the TilePage that is the default page of the site root (automatic) | landing page of the site; the start page of the showcase study (docs/showcase.html in graffiti.theme): hero, search, then the tiles of the page |
| `default-tiles-layout` | the editorial tile pages `/editing` and `/exploring` (field `page_layout`) | the site look with breadcrumbs and the title of the page, without the search of the header and without document actions; search and dashboard are tiles of the page (`default-tiles.css`) |
| `site-layout` | every other page that main_template renders in view mode (no body class; the fallback) | the look of `/exploring` for the whole site: slim blue header, breadcrumbs, search bar above the title, content, blue footer (`site.css`) |

Portlet columns are not part of the new layouts (the content area is always full width).

## Files in `static/`

- `rules.xml`: the dispatcher, exactly one branch per page (iframe views and everything not switched on stay on
  `interaktiv.theme`).
- `site.html`: the one theme file of `site-layout` and `default-tiles-layout` (copy of `authenticated.html` of
  interaktiv.theme).
- `frame.xml`: head, body attributes, toolbar (anonymous and authenticated variants).
- `regions/*.xml`: one rule file per region (`header`, `statusmessage`, `breadcrumbs`, `content`, `footer`,
  `common`), cut from `rules_default.xml` of interaktiv.theme. `regions/omitted-in-default-tiles.xml` lists what
  `default-tiles-layout` leaves out.
- `layouts/<id>/rules.xml`: which of these files a layout includes. `layouts/site-search-layout/` has its own
  theme file.

## How a page gets its layout

- The behavior `openheidelberg.layout.page_layout` (added to the TilePage FTI by the profile) adds the field
  `page_layout` (`site-search-layout`, `default-tiles-layout`, or empty).
- `layout_policy.py` subclasses the TilePage layout policy of interaktiv.basetiles and adds the body class
  `layout-<id>`. A TilePage without a value that is the default page of the site root gets
  `layout-site-search-layout`.
- The two explicit layouts apply in view mode only; in edit mode the tiles editor stays on `interaktiv.theme`.
- `site-layout` is switched on by the theme parameter `site_layout_enabled` (`manifest.cfg`), since 2026-11-04 for
  all visitors (`python:'1'`; read at server start). To go back to the cookie preview use
  `python:'1' if request.cookies.get('openheidelberg_layout') == 'new' else ''` (set the cookie in the browser
  console: `document.cookie = 'openheidelberg_layout=new; path=/'`), or `python:''` to switch it off.
- Styles: `site.css` is the shared look of both layouts that use `site.html` (not scoped to a layout);
  `layouts/default-tiles-layout/default-tiles.css` holds only what the editorial pages add (dashboard, count).

The registration of the layout policy replaces the one of interaktiv.basetiles (same discriminators, in
`overrides.zcml`, which z3c.autoinclude loads for Plone add-ons).

## Setting a layout

Open the TilePage, then "Page" (Page configuration, `edit?settings`) in the toolbar; the field "Page layout" is in
the "Default" fieldset. Choose `Default tiles layout` for the editorial pages (`/editing`, `/exploring`) or
`Site search layout`, then save and look at the page in view mode (not Edit). Empty means: the default page of the
site root gets `site-search-layout`, every other TilePage keeps the standard theme. The plain Edit link opens the
tiles editor, which has no form fields.

## Pitfalls

- The behavior schema `IPageLayout` has to provide `IFormFieldProvider` (`alsoProvides` at the end of
  `interfaces.py`). Without it the behavior is registered, listed as enabled on the TilePage type, and still left
  out of the add and edit forms, without any message.
- Python and ZCML changes need a restart of the instance; changes in `static/` are served from disk.

## Layout matrix

Each cell: `live` (rule included, copy of the current look), `empty` (no rule, not built yet), `omitted` (left
out by design), `dummy` (designer's text). Update it in the same commit as the rule.

| Region | site-search-layout | default-tiles-layout | site-layout |
|---|---|---|---|
| frame (head, bundles, body attributes) | empty | live | live |
| toolbar | empty | live | live |
| hero (logos, lines, title, subtitle) | live (static in the theme file; title from `<title>`, subtitle from `meta[name=description]`) | - | - |
| header | omitted (no header on the start page) | slim (logo left, site actions right; `regions/header-slim.xml`) | slim (same) |
| search | live (form in the theme file, action `@@search`, field `SearchableText`; clear button in `site-search.js`) | omitted (the search is a tile of the page, styled like the start page) | live (search bar above the title, `regions/search-bar.xml`, same look as the tile) |
| status messages | empty | live | live |
| breadcrumbs | empty | live | live |
| document actions | empty | omitted | live (copied; not restyled) |
| content | live (children of `#content-core` in `#start-content`; the sections and cards are tiles) | live | live |
| portlet columns | omitted | omitted | omitted |
| footer | empty | live (blue) | live (blue) |

"live" means the rules of interaktiv.theme were copied; the header, breadcrumbs, search, title, tables and footer are restyled in `site.css`.

## Checked

With the Diazo compiler (offline, interaktiv's rules replaced by a stub, a fake Plone page): site-search view shows
only "Hello world!"; the default-tiles view shows header, content and toolbar but not search, breadcrumbs or
document actions; the site layout shows all of them when switched on and falls back to the stub when not;
edit-mode pages and iframe views fall back. Inside Plone (2026-10-31, as admin, local site): the site root renders the TilePage `search-layout` with only "Hello world!" and the body class `layout-site-search-layout`; the field "Page layout" appears in Page configuration after the `IFormFieldProvider` fix. Not checked inside Plone: the rendering of `default-tiles-layout` and `site-layout`, the cookie preview, anonymous view of the front page. The selectors for search (`#portal-searchbox`), document actions
(`#content .documentActions`) and breadcrumbs (`#portal-breadcrumbs`) were checked against the unthemed
front page of the running site on 2026-10-31.

Start page (2026-11-02, as admin, local site, in the browser pane): `/` shows hero, search and three sections with three cards each; sizes of icon, card title, card description and card were measured in the DOM against `docs/showcase.html` and agree. The look of the sections comes from `openheidelberg.tile_card` (`.tile.tile-frame:has(.tile-card)`), the content from `scripts/setup_demo_start_page.py`. Not checked: the anonymous view, widths up to 768 px, status messages.

The dispatcher `static/rules.xml` uses `css:if-content`, `css:if-not-content` and nested `<rules>` like interaktiv.theme; it was compared offline with the earlier XPath version on 60 test pages (no difference); not yet checked inside Plone.

## Install

Part of `openheidelberg.policy`'s dependencies; apply the profile `openheidelberg.layout:default`. It enables
the theme `openheidelberg.layout`, which includes the rules of `interaktiv.theme` for every other page.
Uninstall re-enables `interaktiv.theme`.
