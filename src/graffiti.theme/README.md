# graffiti.theme

Styles of the Graffiti demo site on top of the default theme `interaktiv.theme`.
The package only brings LESS: no Diazo rules, no templates, no GenericSetup profile.
It is part of the buildout (`buildout.d/base/sources.cfg`), but there is nothing to activate in Plone.

The look of the demo site has two parts:

- **Settings** that a control panel or the editor manages anyway: values of the tiles styleguide (fonts, colors, line heights), the three portlets of the footer, the header images of the main pages, the logo and the favicon.
  The script `scripts/setup_demo_theme.py` sets them, so these control panels keep working.
  Run it with a stopped instance: `bin/instance run scripts/setup_demo_theme.py [site_id]`.
  It runs Grunt afterwards.
- **LESS** in this package for everything these settings do not offer, see below.

Header images, logo and favicon are drawn in code, see [scripts/header_images/README.md](../../scripts/header_images/README.md).

## How it gets into the build

The root `package.json` names the package as theme package:

```json
"interaktiv_setup": {
  "theme_package": "graffiti.theme",
  ...
}
```

Grunt then reads every `src/graffiti.theme/src/graffiti/theme/static/less/*.less` without a leading underscore and puts it into `var/static/css/style.css`, first of all files.
Here that is `graffiti-theme.less`, which imports the partials.
The build runs with `bin/buildout` as usual, see [docs/project/assets-and-styleguide.md](../../docs/project/assets-and-styleguide.md).

Because the theme comes first, its rules lose against rules with the same selector from the tile packages.
Where a rule has to win, it uses a more specific selector (`html:root`, an extra ID), not `!important`.

## What it changes

| File | Change | Plone 5.2.2 | Plone 6.1.2 |
|---|---|---|---|
| `_root-font-size.less` | Root font size from the tiles styleguide (`@global-font-size`, tablet and phone values) | fixes the dialogs of the tiles editor, see below | no change, the root already has these values |
| `_navigation.less` | On the desktop the main menu uses all the space next to the logo instead of 70% of the header, less space between entries up to 1200px | the menu stays in one row with the Plone toolbar open | same |
| `_header.less` | A stripe in the colors of the logo below the header, the main menu in black with a red underline | | same |
| `_content.less` | The information bars of working copies and the lock info get the width of the status messages, text tiles keep lines at a readable length. On tiles pages the byline and the portlet columns get space below the header. Classes for the parts of the demo pages: `lead`, `graffiti-facts` ("At a glance"), `graffiti-links`, `graffiti-step` (numbers of steps), `graffiti-screenshot` | | same |
| `_footer.less` | Colors and spacing of the footer | colors from this file, `interaktiv.layout` 5.x has fixed ones | colors from the tiles styleguide, see below |
| `_leadimage.less` | Text on the header images in the fonts of the site, the button in the colors of the primary button, lower heights: big 540px, medium 400px, small 280px (900, 600 and 470 in `interaktiv.layout`). On phones and tablets the text goes below the image, the focus point of the image keeps the motif in view. No slanted edge below the header of front pages (`interaktiv.layout` adds it to pages named `startseite` or `frontpage`) | | same |

### Root font size on Plone 5

The tile packages write font sizes in `rem` and convert them from px with `@global-font-size` (mixin `.font-size-px`, 16px in the styleguide).
On Plone 5 the root font size ends up at 10px: Barceloneta sets 62.5%, and the Bootstrap 3 import of `interaktiv.theme` 4.x sets 10px after `interaktiv.basetiles`.
Every `rem` value shrinks to 62.5%, labels in the dialogs of the tiles editor get 7.5px instead of 12px, titles 8.75px instead of 14px.
`html:root` outranks the `html` selectors of both.

Side effect: everything else in `rem` grows back to the size it was meant to have, for example the main menu, the headings of Plone forms and the labels of edit forms.

### Defaults that the styleguide overrides on Plone 6

From `interaktiv.basetiles` 29 on the tiles styleguide also has colors for the footer and fonts and colors for the text on header images.
`_footer.less` and `_leadimage.less` define these LESS variables with the values of the demo site.
LESS takes the last definition of a variable, and the styleguide comes after this package.
So on Plone 6 the values of the control panel win, on Plone 5 these defaults count.

## For projects

A project with its own theme package does not need `graffiti.theme`.
If it uses `interaktiv.theme` 4.x without its own theme on Plone 5, it needs the same root font size rule, otherwise the dialogs of the tiles editor stay too small.
