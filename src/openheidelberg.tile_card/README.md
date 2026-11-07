# openheidelberg.tile_card

Cards

Cards are rectangular containers that bundle related information — an image, a title, a short description, and an action. They work well for grid layouts of similar items (product listings, team members, blog posts). Cards should have clear boundaries (shadow or border) and a single primary action.

## What the tile does

Portal type `TileCard`, tile id `openheidelberg_tile_card`, label "Card". Fields:

- `title` (required), `description` (short text)
- `image` (relation to an Image) and `image_alt`
- one primary action: `link_href` (full URL or a path starting with `/`), `link_label`, `link_new_window`, `link_show_button`.
  With `link_show_button` off (default on) there is no button: the title becomes the link and the whole card stays
  clickable. Cards created before the option existed keep their button.
- an optional vector icon: `card_icon_svg`, the name of one icon of the icon registry (see below), shown beside the
  title, and `card_icon_orientation` for its position (`title`, the default, `left` or `right`). `left`/`right` put the
  icon in a column beside the title and the description together, spanning both; `title` puts it beside the title
  only, with the description below. Without a vector icon the card uses the plain layout and leaves no room for one.
  The description starts at the same height in all positions.
- an optional action icon: `card_icon`, a glyph of the icon fonts of interaktiv.basetiles and its font families. It
  replaces the arrow at the bottom right of the card; without it the default arrow stays.

The "Edit card" dialog has an "Icon" tab with the position select, the picker of the vector icons and the action
icons.

## Vector icon registry

The vector icons are kept in the `plone.registry` record `openheidelberg.tile_card.svg_icons` (a dictionary from name
to SVG markup); until something is saved, the files bundled in `static/icons` are used. The control panel
"Card tile SVG icons" (`@@tile-card-svg-icons`, section "Mosaik Tiles" of the Site Setup overview) adds icons by
pasted markup or uploaded `.svg`, replaces and deletes them, and restores missing bundled icons. Markup passes
`svg_sanitizer.py` (whitelist of elements and attributes; no script, style, `url()`, `data:` or DOCTYPE). An icon that
a tile uses (published or working copy) is listed with its pages and cannot be deleted.

Editing happens in a small modal ("Edit card" in the tile's tool bar, page `@@configure_tilecard_modal`) that
saves through the generic `update_content` API of interaktiv.basetiles. Background, padding, vertical
alignment and anchor come from the basetiles behaviors. The card boundary (border and soft shadow) is defined in
`static/css/tile.css`.

## Activate after an update

Because the add-on was already installed as a dependency of `openheidelberg.policy`, restart `bin/instance fg`, then
run the upgrade step of the profile (Site Setup, Add-ons, Upgrades: `openheidelberg.tile_card` 0003 -> 0004
registers the script bundle; earlier versions 0001 -> 0003 add the control panel and its section) or re-apply the profile `openheidelberg.tile_card:default` (Site Setup, Add-ons, or ZMI
`portal_setup`, Import, profile `openheidelberg.tile_card`). The tile registration happens in the profile's post
handler. No buildout and no Grunt run are needed for this package.

## Look of the card

The look of a card (box, border and shadow, padding, title and description typography, the arrow at the bottom right,
hover) is defined by `tile.css` on the card itself. It does not depend on the theme or on where the card stands (in
a row of the page or in a frame). The title and description rules also exist with the prefix `#content-core`, which
outranks the ID selectors of the theme's `h3` and `p`. Only the section box (a frame tile that contains cards, with its
heading) is tied to the frame: `.tile.tile-frame:has(.tile-card)`. The arrow is shown only when the card has no button
(`has-action-button` on `.card-body`); an action icon replaces it.

## Image and layout in a row

The image sits in a fixed 16:9 frame (`aspect-ratio`) and is cropped with `object-fit: cover`, so cards in
one row stay equally tall whatever the image proportions. The description is clamped to four lines. The action
link stretches over the whole card (`::after`), so the card as a whole is the click target, which gives
news-style grids a single primary action per card. The image scale is `@@images/image/large`.

## Plain CSS and JavaScript bundles

`static/css/tile.css` is the only stylesheet of the tile (there is no LESS file in this branch). It is registered as
the Plone bundle `openheidelberg-tile-card` (`profiles/default/registry.xml`) and served from the resource directory
`++resource++openheidelberg.tile_card/css/tile.css` without compilation, so a reload shows edits without buildout or
Grunt. The bundle adds one `<link>` per page (not per tile) and only on tiles pages.

The script of the "Edit card" dialog, `static/js/modal_configure.js`, is served the same way: the bundle
`openheidelberg-tile-card-js` (`jscompilation`, `compile` off) points at
`++resource++openheidelberg.tile_card/js/modal_configure.js`. It is not part of the Grunt build, because the package
is not listed in `interaktiv_setup.packages` (its `package.json` lists none, and the root `package.json` does not
name it). basetiles looks `initializeConfigureTileCardModal` up on `window` when the dialog opens, so the file only has
to define it as a global function; the load order does not matter. For debugging, edit the file and reload hard.
