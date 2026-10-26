# Custom CSS classes for the button tile

Version 1.1 (30.09.2026), changes in [CHANGELOG.md](CHANGELOG.md)

Editors who may style a button tile add their own CSS classes to the button link, in a tab "CSS classes" of the button dialog.
A project attaches behaviour to a class, for example `pat-plone-modal` opens the link target in a Plone modal, or its own JavaScript opens a dialog of the project.
The demo page "Entry page for authors" ends with such a button, it opens the FAQ of the folder in a modal.

The package `graffiti.tile_button` changes `interaktiv.tile_button` 10.x (Plone 5.2) and 15.x (Plone 6.1) from the outside, the button tile itself stays as it is.
From `interaktiv.tile_button` 16.3.0 (Plone 6.2) on, the button tile has the feature itself, with presets in its settings, and the package is no longer needed.
Everything else lives with the package, with screenshots, the switch in the registry and what to adjust after an update of the button tile: [src/graffiti.tile_button/README.md](../../../src/graffiti.tile_button/README.md).
