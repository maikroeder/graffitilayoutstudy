# Header images, logo and favicon of the demo site

The JPGs in this folder are the header images of the main pages of the demo site, `logo.png` and `favicon.ico` are the logo and the favicon.
`scripts/setup_demo_theme.py` uploads the header images into the folder "demo-images" and sets them as header of the pages.
It sets the logo in the site settings of Plone and the favicon where the favicon settings of `interaktiv.theme` keep it.

They are drawn in code, there is no photo and no third-party material in them: a dark wall, spray paint in the colors of the Graffiti logo and one motif per page.
The logo writes "Graffiti" in Lato Bold, the font of the headings of the site (SIL Open Font License, from `interaktiv.basetiles`).
They are under the same license as the rest of the repository.

| Image | Page | Motif |
|---|---|---|
| `header-home.jpg` | front page | a spray can that sprays the colors of the logo |
| `header-entry-authors.jpg` | entry page for authors | a pencil on a stack of documents |
| `header-working-copies.jpg` | working copies | the original and its copy side by side, the changed lines marked |
| `header-search.jpg` | search page | a magnifying glass over lines of text |
| `header-pdf-check.jpg` | PDF check | a PDF document with a folded corner and a stamp with a check mark |
| `header-mcp-demo.jpg` | MCP demo documents | speech bubbles connected to a document |
| `header-webmirror.jpg` | WebMirror | a website in a frame in a frame |
| `logo.png` | every page | the spray can of the front page on a dark tile, and "Graffiti" |
| `favicon.ico` | every page | the spray can on the dark tile, 16, 32 and 48 px |

## Drawing them again

1. `make_header_images.py` writes one SVG per image: 2400 x 800 px for the header images, 1000 x 300 px for the logo, 256 x 256 px for the favicon.
   The random parts use a fixed seed, so every run draws the same pictures.
   The logo needs the checkout of `interaktiv.basetiles` under `src/`, the script embeds its Lato Bold.
2. `render.js` turns the SVGs into PNGs with Chromium, which shows the SVG filters (wall texture, spray, rough edges) as a browser does.
   It needs Playwright.
3. ImageMagick makes JPGs of the header images, cuts the empty edge off the logo and makes the favicon.

```shell
python3 scripts/header_images/make_header_images.py /tmp/header-images
node scripts/header_images/render.js /tmp/header-images
for f in /tmp/header-images/header-*.png; do convert "$f" -strip -quality 82 "scripts/header_images/$(basename "${f%.png}").jpg"; done
convert /tmp/header-images/logo.png -trim +repage scripts/header_images/logo.png
convert /tmp/header-images/favicon.png -define icon:auto-resize=48,32,16 scripts/header_images/favicon.ico
```

The left part of every header image is darker on purpose: title and text of the header sit there.
Smaller headers (280px high) only show the middle band of the image, so the motifs of the pages other than the front page are drawn smaller.
The motifs stand on the right, so the setup script gives the header images a focus point there: phones and tablets show that part above the text.
