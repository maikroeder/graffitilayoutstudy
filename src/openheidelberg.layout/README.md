# openheidelberg.layout

Page layouts for the OpenHeidelberg site on top of Plone's `main_template`: a Diazo theme with one theme file
per layout, and a behavior that lets a TilePage choose its layout.

Status: structure in place, checked offline with the Diazo compiler on a Plone-like test page (see "Checked");
not yet installed or run in Plone.

## Layouts

| Id | Used by | What it is |
|---|---|---|
| `site-search-layout` | the TilePage that is the default page of the site root (automatic) | landing page of the site; the start page of the showcase study (docs/showcase.html in graffiti.theme): hero, search, then the tiles of the page |
| `site-layout` | every other page that main_template renders in view mode, `/exploring` and `/editing` included (no body class; the fallback) | the look of `/exploring` for the whole site: slim blue header, breadcrumbs, search bar above the title, content, blue footer (`site.css`) |
| `site-edit-layout` | edit mode of tile pages (body class `edit-mode`), when `site_layout_enabled` is on | the frame of the site (slim header, breadcrumbs, blue footer) around the tiles editor; no search bar, no extra title |

Portlet columns are not part of the new layouts (the content area is always full width).

## Files in `static/`

- `rules.xml`: the dispatcher, exactly one branch per page (everything not switched on stays on `interaktiv.theme`). A branch for
  pages with an element of the class `.iframe-view` was removed on 2026-11-09: no code in `src/` sets that class.
- `site.html`: the one theme file of `site-layout` (copy of `authenticated.html` of
  interaktiv.theme).
- `frame.xml`: head, body attributes, toolbar (anonymous and authenticated variants).
- `regions/*.xml`: one rule file per region (`header`, `statusmessage`, `breadcrumbs`, `content`, `footer`,
  `common`), cut from `rules_default.xml` of interaktiv.theme. `regions/omitted-with-search-tile.xml` drops header search, document actions and byline of a page
  whose content has its own `.tile-search` (/exploring, /editing); `search-bar.xml` skips such pages too.
- `layouts/<id>/rules.xml`: which of these files a layout includes. `layouts/site-search-layout/` has its own
  theme file.

## How a page gets its layout

- The behavior `openheidelberg.layout.page_layout` (added to the TilePage FTI by the profile) adds the field
  `page_layout` (`site-search-layout` or empty).
- `layout_policy.py` adds the body class `layout-<id>` to the body class of the policy of the page, through a mixin
  (`LayoutClassMixin`) used by two classes: `OpenHeidelbergTilePageLayoutPolicy` (subclass of the TilePage policy of
  interaktiv.basetiles, so `view-mode`, `edit-mode`, `is-tilepage` stay) and `OpenHeidelbergLayoutPolicy` (subclass of
  `plone.app.layout.globals.layout.LayoutPolicy`, for all other content). An object without a value of `page_layout`
  that is the default page of the site root gets `layout-site-search-layout`. The class is only added in view mode
  (the default view is shown, `plone_context_state.is_view_template()`; for TilePages also: not edit mode). The sharing and portlet pages of a page therefore keep the site layout.
- The explicit layout applies in view mode only; in edit mode a tile page gets `site-edit-layout` (frame of the site, editor and toolbar as before) while the switch is on, and `interaktiv.theme` when it is off.
- `site-layout` is switched on by the theme parameter `site_layout_enabled` (`manifest.cfg`), since 2026-11-04 for
  all visitors (`python:'1'`; read at server start). To go back to the cookie preview use
  `python:'1' if request.cookies.get('openheidelberg_layout') == 'new' else ''` (set the cookie in the browser
  console: `document.cookie = 'openheidelberg_layout=new; path=/'`), or `python:''` to switch it off.
- Styles: `base.css` holds what the start page and the other pages share (colour and shadow tokens, the typeface with its `!important` against `style.css` of the theme); both theme files link it first. `site.css` is the look of the whole site except the start page (not scoped to a layout; it includes the dashboard tile and the document count);
  the start page has its own `layouts/site-search-layout/site-search.css`. /exploring and /editing are ordinary pages. A stored `page_layout` value `default-tiles-layout` is ignored.

`overrides.zcml` (loaded by z3c.autoinclude for Plone add-ons) registers both classes under the view name `plone_layout`:
the TilePage one replaces the one of interaktiv.basetiles (same discriminators), the other is registered for `*` on the
layer `IOpenHeidelbergLayoutLayer`. Status 2026-11-09: written, not yet run in Plone (needs a restart).

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

| Region | site-search-layout | site-layout |
|---|---|---|
| frame (head, bundles, body attributes) | empty | live |
| toolbar | empty | live |
| hero (logos, lines, title, subtitle) | live (static in the theme file; title from `<title>`, subtitle from `meta[name=description]`) | - |
| header | omitted (no header on the start page) | slim (same) |
| search | live (form in the theme file, action `@@search`, field `SearchableText`; clear button in `site-search.js`) | live (search bar above the title, `regions/search-bar.xml`, same look as the tile) |
| status messages | empty | live |
| breadcrumbs | empty | live |
| document actions | empty | live (copied; not restyled) |
| content | live (children of `#content-core` in `#start-content`; the sections and cards are tiles) | live |
| portlet columns | omitted | omitted |
| footer | empty | live (blue) |

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
