# Changes

Version and date are at the top of every file in this folder and in the handover PDF with the client.
New versions go on top.

## 1.10 (22.10.2026)

- The demo page has the layout of the topic pages of the demo site: what an entry page is, "At a glance", numbered steps, then the example on a light background in columns with headings, and "How it works". The screenshots 01 to 05 still show the earlier layout.
- The demo script deletes only its own folder `entry-authors`. The earlier folder `einstieg-autoren` is no longer removed, delete it by hand if a site still has it.

## 1.9 (30.09.2026)

- New: package `graffiti.tile_button`. The dialog of the button tile gets a tab "CSS classes", editors who may style the tile add their own classes to the button link. A project attaches behaviour to a class, for example a Plone modal through `pat-plone-modal` or its own dialog. It changes `interaktiv.tile_button` 10.x and 15.x from the outside, a registry record switches it off.
- The demo page ends with a button that opens the FAQ of the folder in a Plone modal, the FAQ has example questions and answers.
- Screenshots 01, 03, 04 and 05 renewed, they show the button at the end of the page. The feature has its own folder now: [button-css-classes](../button-css-classes/README.md).

## 1.8 (28.09.2026)

- Folder moved to `docs/features/entry-pages`, all feature folders now live under `docs/features/`.
- English labels in the tiles editor aligned with the documentation: "Tab lists" (was "Tabbed lists") and "Embedded view" (was "View"). Translations decide what editors see, English sites need the compiled `.mo` files.
- Screenshots 06 and 07 renewed with the English demo page, 01 to 05 with the site logo. Highlights mark the spots to look at, also in the READMEs of the packages.

## 1.7 (28.09.2026)

- Every package has a README with screenshots: what editors see, what decides the content, package layout, installation, tests. Linked from the table "Where things live".
- The demo page is in English: folder `entry-authors`, page `entry`, five example documents. The script also removes the earlier folder `einstieg-autoren`.
- The example view of the view tile shows the date in the format of the site language.
- Screenshots 01 to 05 renewed with the English demo page, 06 and 07 (tiles with and without CSS) still show the German one.
- The mode `ajax_load` of the view tile is called an interim solution everywhere now, in the editor as well.

## 1.6 (28.09.2026)

- Documentation in English, folder renamed to `docs/entry-pages`, files renamed (`interfaces.md`, `adoption.md`).
- The five packages are merged into `main` (Plone 5.2) and `21170-migrate_to_plone6` (Plone 6), the two feature branches are gone.

## 1.5 (28.09.2026)

- New: `adoption.md` walks through adopting the tiles in a target project: check the requirements, add the packages, check the assets, tile without styling. With the script `scripts/check_tiles_assets.py`, which checks without Zope whether CSS and JavaScript of the tiles are built and up to date.
- New: `docs/project/assets-and-styleguide.md` explains how CSS and JavaScript of the tiles are built and delivered, the control panel "Tiles-Styleguide" and building without internet access. For Plone 5.2 and Plone 6.

## 1.4 (24.09.2026)

- New: `scripts/check_tiles_requirements.py` checks in another Plone environment whether everything the five tiles need from `interaktiv.basetiles` and `interaktiv.framework` is there (imports, methods, views, portal types). The frame tile of the editor is not part of it.

## 1.3 (23.09.2026)

- Dashboard: a box can declare itself urgent (key `urgent`). With more than 0 entries it turns red and shows a task list icon (replaceable with CSS). Every box decides that itself. Default adapter: collections tagged `todo`.
- The demo `graffiti.stage.interaktiv.de` runs this state again.

## 1.2 (23.09.2026)

- New: tile "Tab lists" (`graffiti.tile_tabs`), several lists in tabs. Interface `ITabListsProvider`.
- New: tile "Embedded view" (`graffiti.tile_view`), editors pick a view registered by the developer. Interface `IEmbeddableViewsProvider`, modes `view` and `ajax_load`.
- Search: the name of the search parameter is configurable (`get_search_parameter_name()`), the default stays `SearchableText`.
- Finding added: embedding existing pages works as an interim solution, with limits (`evaluation.md`, findings).
- The demo page creates five tiles, screenshots renewed, 100 tests per version.

## 1.1 (22.09.2026)

- Plone 5.2.2 (the state of `main`) is supported. Second branch from `main`, merge request into `main`.
- Three adjustments for Plone 5.2 (imports, namespace, behavior paths), see `interfaces.md`, section Requirements.
- Search: size of title and description in the live results protected against the tiles theme.

## 1.0 (21.09.2026)

- First handover: folder listing, search and dashboard as placeholder tiles (variant A), adapter interfaces with contract tests, demo page, handover PDF with the client. Verified on Plone 6.1.2.
- Documentation condensed, open questions only with the client.
