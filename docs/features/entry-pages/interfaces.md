# Interfaces

Version 1.10 (22.10.2026), changes in [CHANGELOG.md](CHANGELOG.md)

A project adopts the tiles unchanged and still decides what they show.
It registers its own adapters and touches neither views nor templates.

## The pattern

Every tile asks exactly one adapter on (tiles page, request).

| Tile | Interface | Default adapter |
|---|---|---|
| Folder listing | `graffiti.tile_listing.interfaces.IListingItemsProvider` | Content of the folder of the page |
| Search | `graffiti.tile_search.interfaces.ISearchTileSettings` | Plone's search for the whole site |
| Dashboard | `graffiti.tile_dashboard.interfaces.IDashboardBoxesProvider` | One box per collection in the folder of the page |
| Tab lists | `graffiti.tile_tabs.interfaces.ITabListsProvider` | Three tabs from the catalog: recently changed, created by me, in this folder |
| Embedded view | `graffiti.tile_view.interfaces.IEmbeddableViewsProvider` | Three examples: a frameless view of the package, the search page and the sitemap of Plone |

The default adapters are registered for `(ITilePage, Interface)`, that is for every request.
A project registers its adapter for `(ITilePage, <its own browser layer>)`.
The more specific layer wins as soon as the project add-on is installed in the site.

```python
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from myproject.interfaces import IMyProjectLayer
from zope.component import adapter
from zope.interface import implementer


@implementer(IDashboardBoxesProvider)
@adapter(ITilePage, IMyProjectLayer)
class ProjectBoxesProvider:

    def __init__(self, context, request):
        self.context = context  # the tiles page
        self.request = request

    def get_boxes(self):
        return [{'id': 'todo', 'title': 'My tasks', 'description': '', 'url': 'https://example.org/todo'}]

    def get_counts(self):
        return {'todo': 42}
```

```xml
<adapter factory=".dashboard.ProjectBoxesProvider" />
```

The adapter knows the tiles page and the request.
From these it derives what should drive the display: the folder of the page, the logged-in user, their roles and groups.

## Folder listing: `IListingItemsProvider`

| Method | Returns | Called |
|---|---|---|
| `get_label()` | `str`, short text for the placeholder in the editor | In the editor |
| `get_items()` | `list` of `dict` with `title`, `description`, `url`, `portal_type` (all `str`), only entries the user may see | On every render |

`portal_type` is only used for the CSS class `contenttype-<type>`, custom type names are allowed.

Default: catalog query on the folder of the page, depth 1, sorted by folder position.
The tiles page itself and content with "Exclude from navigation" are left out.
There is no batching.

## Search: `ISearchTileSettings`

| Method | Returns | Meaning |
|---|---|---|
| `get_search_url()` | `str`, absolute | Target of the form (GET) |
| `get_search_parameter_name()` | `str`, a plain name | Name of the parameter that carries the search term. Default `SearchableText`, a custom search page gets `q`, for example |
| `get_livesearch_url()` | `str` or `None` | Address for `pat-livesearch`, returns JSON in the format of Plone's `@@ajax-search`. `None` switches the live results off |
| `get_parameters()` | `dict` of `str` to `str` | Fixed extra parameters as hidden fields, for example `{'path': '/site/documents'}`. The search parameter must not be included |

The extra parameters do not apply to the live results.
If the live results should be restricted as well, the address from `get_livesearch_url()` has to do that itself.

## Dashboard: `IDashboardBoxesProvider`

| Method | Returns | Called |
|---|---|---|
| `get_boxes()` | `list` of `dict` with `id`, `title`, `description`, `url` (all `str`), `id` is unique on the page. Optional `urgent` (`bool`) | On every render, also in the editor. Must be cheap, do not calculate numbers here |
| `get_counts()` | `dict` of box `id` to an integer from 0, calculated for the logged-in user | After rendering, by JavaScript. May be more expensive |

If `get_boxes()` returns an empty list, visitors do not see the tile.

`urgent`: a box with `urgent: True` turns red and shows a task list icon in the top right corner as soon as its number is above 0.
At 0 it looks like every other box.
Every box decides that for itself, without the key nothing changes.
`static/js/tile.js` switches the state after loading the numbers (class `is-urgent` on the box).
The icon comes from CSS: `.tile-dashboard-todo::before` with a mask from a data URI, it takes the color of the box.
A project replaces it with its own rule, for example:

```css
.tile-dashboard .tile-dashboard-todo::before {
  mask-image: url("/++theme++myproject/icons/tasks.svg");
  -webkit-mask-image: url("/++theme++myproject/icons/tasks.svg");
}
```

An icon font works the same way: `mask: none; background: none; content: "\f0ae"; font-family: ...`.

Flow in the browser: the page contains the boxes without numbers.
`static/js/tile.js` calls `<address of the tiles page>/@@tile_dashboard_data`.
The answer is `{"counts": {"<box id>": 3}}` with `Cache-Control: private, no-store`.
Afterwards the tile carries the class `tile-dashboard-loaded`, on an error `tile-dashboard-failed`.

Default: every collection in the folder of the page is a box, the number is its result count for the logged-in user.
A collection tagged `todo` is an urgent box, editors decide that without code.
The relation to the user comes from Plone's permission checks and from criteria like "creator is the current user".

## Tab lists: `ITabListsProvider`

For areas that show several lists under tabs, for example newest documents, saved searches and favorites.
The tile renders everything server side as tables, a small script switches the tabs.

| Method | Returns | Called |
|---|---|---|
| `get_tabs()` | `list` of `dict`, one entry per tab in display order | On every render, also in the editor |

A tab has exactly these keys:

| Key | Content |
|---|---|
| `id` | `str`, unique within the tile, ends up in HTML attributes |
| `title` | `str`, label of the tab |
| `columns` | `list` of `dict` with `id` (unique within the tab) and `title` |
| `rows` | `list` of `dict` with `url` (link of the first column, may be empty) and `cells`, a `dict` from column `id` to text |
| `empty_text` | `str`, shown in the tab when `rows` is empty |

Only rows the user may see.
If `get_tabs()` returns an empty list, visitors do not see the tile.
The first tab is open, the other panels carry `hidden`.
`static/js/tile.js` switches the tabs through a handler on the document, a tile needs no initialization.

Default: three tabs with the columns title, type and changed, at most ten rows each from the catalog.
"Created by me" is empty for visitors.

## Embedded view: `IEmbeddableViewsProvider`

For areas that already exist as a view in the project.
A developer registers the allowed views, editors pick one of them in the tile (gear icon in the editor).
The tile stores only the `id` of the choice.

| Method | Returns | Called |
|---|---|---|
| `get_views()` | `list` of `dict` with `id`, `title`, `description`, `url`, `mode` (all `str`) | On every render and in the selection dialog |

`url` is absolute and inside the site.
The tile fetches it with `plone.subrequest` in the same request, that is with the same user and their permissions.
`mode` decides what happens with the answer:

| `mode` | Expectation on the view | What the tile does |
|---|---|---|
| `view` | Frameless view, returns an HTML fragment without `<html>` and without the page frame | Insert the fragment unchanged. If the view answers with a whole page, that counts as an error |
| `ajax_load` | An ordinary page. Plone renders it with `ajax_load=1` without navigation, columns and footer | Cut out `#content-core` (otherwise `#content`), remove the ids of the page frame, strip `ajax_load` from links and form targets |

`ajax_load` is an interim solution: the page does not bring its own CSS and JavaScript, but `<script>` tags inside the content area do run.
Everything that depends on ids of the page frame or on Bootstrap classes of the theme does not work inside the tile.
New areas belong in a frameless view with `mode` `view`.

Error cases: if the chosen `id` is no longer registered, the view does not answer with status 200, or a `view` view returns a whole page, visitors see an empty tile and the log gets a warning.
In the editor the placeholder shows title and description of the choice, the view is not rendered there.

Default: three examples.
`example-recent` is the frameless view `@@tile-view-example-recent` of this package (mode `view`), `plone-search` and `plone-sitemap` are Plone's search page and sitemap (mode `ajax_load`).

## Contract tests

Every package ships a mixin class with tests in `contract.py` that a project applies to its own adapter.

```python
from graffiti.tile_dashboard.contract import DashboardBoxesProviderContract
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from zope.component import getMultiAdapter


class TestMyBoxes(DashboardBoxesProviderContract, MyProjectTestCase):
    layer = MY_PROJECT_FUNCTIONAL_TESTING

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), IDashboardBoxesProvider)
```

| Mixin | The project provides | Checked |
|---|---|---|
| `graffiti.tile_listing.contract.ListingItemsProviderContract` | `get_provider()` | Interface satisfied, entries have exactly the four keys as text, title and address are not empty |
| `graffiti.tile_search.contract.SearchTileSettingsContract` | `get_settings()` | Interface satisfied, addresses are absolute or `None`, the parameter name is a plain name, parameters are text without the search parameter |
| `graffiti.tile_dashboard.contract.DashboardBoxesProviderContract` | `get_provider()` | Interface satisfied, boxes have exactly the four keys as text (plus at most `urgent` as `bool`), ids are unique, every box has exactly one integer from 0 |
| `graffiti.tile_tabs.contract.TabListsProviderContract` | `get_provider()` | Interface satisfied, tabs and columns have exactly their keys and unique ids, cells match the columns, all values are text |
| `graffiti.tile_view.contract.EmbeddableViewsContract` | `get_provider()` | Interface satisfied, entries have exactly the five keys, ids are unique, the mode is known, and every entry renders to a fragment without `<html` and without `id="content"` |

Not checked: that `get_boxes()` is cheap and that only visible entries are returned.
Complete examples with a project layer are in the tests of the packages (`tests/test_provider.py`, `tests/test_settings.py`, `tests/test_view.py`).

## Requirements

- Plone 5.2.2 (Python 3.8, `interaktiv.basetiles` v10, `interaktiv.framework` v7) or Plone 6.1.2 (Python 3.11, `interaktiv.basetiles` v29, `interaktiv.framework` v14).
  Both are verified with the tests and in the browser.
- `jQuery` as global `$` and Plone's JavaScript bundle with `pat-livesearch` on tiles pages.
- For the view tile `plone.subrequest` and `lxml`, both part of Plone.
- The packages are checkouts under `src/`, listed in the asset build (`interaktiv_setup.packages` in `package.json`) and installed in the site. How the build works is described in [../project/assets-and-styleguide.md](../../project/assets-and-styleguide.md), the check for a target project in [adoption.md](adoption.md).
- Tiles pages have no portlet columns.
- Every tile brings five permissions (`InteraktivTiles: Add|Delete|Move|Modify|Style <Name>Tile`), assigning them to roles is not part of the packages.

Whether another environment meets these requirements is checked by a script, see [adoption.md](adoption.md).
The frame tile (`TileFrame`) of the editor is not a requirement.

To run on both versions, the packages follow three rules:

- Imports from `plone.base` fall back to `Products.CMFPlone`.
- The namespace `graffiti` is declared in `src/graffiti/__init__.py` with `declare_namespace` and listed as `namespace_packages` in `setup.py`.
  Without that entry `z3c.autoinclude` (Plone 5.2) does not find the package and does not load its ZCML.
- The FTIs reference the behaviors of `interaktiv.basetiles` by interface path (`interaktiv.basetiles.behaviors.background.IBackgroundBehavior`), not by the short names that only exist from v29 on.

Kept stable: the five interfaces, the type names `TileListing`, `TileSearch`, `TileDashboard`, `TileTabs`, `TileView`, the field `view_id` of the view tile and `@@tile_dashboard_data` with its JSON format.
Templates, CSS classes and JavaScript may still change.
