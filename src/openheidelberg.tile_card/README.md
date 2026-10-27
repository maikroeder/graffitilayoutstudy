# openheidelberg.tile_card

Cards

Cards are rectangular containers that bundle related information — an image, a title, a short description, and an action. They work well for grid layouts of similar items (product listings, team members, blog posts). Cards should have clear boundaries (shadow or border) and a single primary action.

Status: skeleton only; no tile behaviour implemented yet.

Structure to follow `graffiti.tile_button` / `graffiti.tile_listing` in `src/`: content type, interfaces,
adapters, views, GenericSetup profiles.

## What the tile does

Portal type `TileCard`, tile id `openheidelberg_tile_card`, label "Card". Fields:

- `title` (required), `description` (short text)
- `image` (relation to an Image) and `image_alt`
- one primary action: `link_href` (full URL or a path starting with `/`), `link_label`, `link_new_window`, `link_show_button`.
  With `link_show_button` off (default on) there is no button: the title becomes the link and the whole card stays
  clickable. Cards created before the option existed keep their button.
- an optional icon (`card_icon`, from the icon fonts of interaktiv.basetiles and its font families) and
  `card_icon_orientation` (`left`, the default, `right`, or `title`). `left`/`right` put the icon in a column beside the title and the
  description together, spanning both; `title` puts it beside the title only, with the description below
  starting at the icon's left edge. The "Edit card" dialog has an "Icon" tab for it.

Editing happens in a small modal ("Edit card" in the tile's tool bar, page `@@configure_tilecard_modal`) that
saves through the generic `update_content` API of interaktiv.basetiles. Background, padding, vertical
alignment and anchor come from the basetiles behaviors. The card boundary (border and soft shadow) is defined in
`static/css/tile.css`.

## Activate after an update

Because the add-on was already installed as a dependency of `openheidelberg.policy`, run
`./bin/buildout -c stage.cfg` (the Grunt part collects the modal JS), restart `bin/instance fg`, then
re-apply the profile `openheidelberg.tile_card:default` (Site Setup, Add-ons, or ZMI `portal_setup`, Import,
profile `openheidelberg.tile_card`). The tile registration happens in the profile's post handler.

## Image and layout in a row

The image sits in a fixed 16:9 frame (`aspect-ratio`) and is cropped with `object-fit: cover`, so cards in
one row stay equally tall whatever the image proportions. The description is clamped to four lines. The action
link stretches over the whole card (`::after`), so the card as a whole is the click target, which gives
news-style grids a single primary action per card. The image scale is `@@images/image/large`.

## Plain CSS bundle

`static/css/tile.css` is the only stylesheet of the tile (there is no LESS file in this branch). It is registered as
the Plone bundle `openheidelberg-tile-card` (`profiles/default/registry.xml`) and served from the resource directory
`++resource++openheidelberg.tile_card/css/tile.css` without compilation, so a reload shows edits without buildout or
Grunt. The bundle adds one `<link>` per page (not per tile) and only on tiles pages.
