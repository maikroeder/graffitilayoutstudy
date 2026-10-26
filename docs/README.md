# Graffiti documentation

Graffiti is the showcase site of Interaktiv GmbH for the Interaktiv Tiles Editor.
New features for the editor are born here, as packages that other Plone projects can adopt.
That is why the documentation has two threads.

## The project: set up, build, roll out

The local installation is described in the [main README](../README.md).
The pages under `project/` build on that:

- [Installing Plone on separate servers](project/server-installation.md): the ZEO server and Solr on one host, Plone on another, an SSH tunnel in between.
- [CSS and JavaScript of the tiles: build and styleguide](project/assets-and-styleguide.md): the way from the LESS in the package to the page, Plone 5 and 6, the control panel "Tiles-Styleguide", building without internet access, what to check when styles are missing.
- [Updating the demo environment graffiti.stage.interaktiv.de](project/update-demo-environment.md): only relevant for Interaktiv, rolling out a new state over SSH.

## The features: one folder per feature

Every feature that a project can adopt has its own folder.
The entry pages have the full structure: result and how to try it (README), interfaces for your own adapters, adoption in your project, evaluation, changes.
The other folders start thin with a README and the changes.

- [Entry pages with placeholder tiles](features/entry-pages/README.md): folder listing, search, dashboard, tab lists and an embedded view as tiles whose content the project decides through adapters.
- [Custom CSS classes for the button tile](features/button-css-classes/README.md): editors add their own classes to a button, a project attaches behaviour to them, for example a Plone modal. The documentation lives in the package `graffiti.tile_button`.
- [PDF check on upload](features/pdf-check/README.md): Plone checks uploaded PDF files whether they can be processed later, warns the editor and stores the result for workflows, without ever rejecting the upload. The documentation lives in the package `graffiti.pdfcheck`.
- [Exact search with Solr](features/exact-search/README.md): the placeholder `{raw_value}` for the search pattern of `collective.solr` and two anchored field types, so that exact titles come first.
- [WebMirror](features/webmirror/README.md): a ZIP with a static website as a content object, shown inside the Plone layout.
- [Working copies with a comparison](features/working-copies/README.md): check out, compare, check in and cancel on the basis of `plone.app.iterate`. The documentation lives in the package `interaktiv.workingcopy`.

## Other

`images/` holds the logo and the screenshots of the main README and the project pages, `examples/` the example ZIP for WebMirrors.
