# TODO

## Search results page: `Unknown sort_on index: ''` (found 2026-11-08)

Symptom: `/@@search?SearchableText=test` shows "No results were found"; the log has a `CatalogError: Unknown sort_on index: ''`
(traceback: `plone.restapi.services.search.get` -> `plone.restapi.search.handler` line 80 -> `collective.solr.monkey.searchResults`
-> `collective.solr.dispatcher` -> `Products.ZCatalog.Catalog._getSortIndex`).

Cause, as observed in the browser pane (logged in, local site):

- The results page loads `++resource++collective.solr.static/dist/search.min.js`.
- It requests `/Plone/@search?metadata_fields=Creator&metadata_fields=modified&sort_on=&SearchableText=test`; the empty
  `sort_on` is what the "relevance" option of the sort dropdown sends.
- `@search?SearchableText=test` returns 200 with items; `...&sort_on=modified` returns 200; `...&sort_on=` returns 500.
- The same request is sent with `?diazo.off=1` (no theme), so it does not come from `openheidelberg.theme`.

Not checked: whether it happened before 2026-11-08; whether it depends on Solr being up locally (the traceback goes through
the dispatcher into the plain catalog).

Options:

1. Check the installed versions of `collective.solr` and `plone.restapi` and the newer releases of `collective.solr`
   for a fix (do this first).
   Checked 2026-11-09: the buildout pins `collective.solr` 8.4.2 and `plone.restapi` 7.0.0 (`buildout.d/base/versions.cfg`). The
   newest `collective.solr` is 9.3.0 (2024-02-15); a summary of its changelog (socket.dev, not the changelog itself) lists no entry about
   `sort_on`, relevance sorting or `@search` after 8.4.2. So no fix is known; 9.x was not tried, and whether it fits this Plone
   version was not checked.
2. Drop an empty `sort_on` before the catalog call (patch or subscriber before the `collective.solr` dispatcher; the
   place is `plone.restapi/search/handler.py`).
3. Change `search.min.js` or its source so that the relevance option sends no `sort_on`.
