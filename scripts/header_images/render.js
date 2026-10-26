// Render every SVG of a folder to PNG with Chromium, so that the SVG filters look as in the browser.
// Usage: node render.js <folder>   (Playwright has to be installed)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const folder = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const name of fs.readdirSync(folder).filter(name => name.endsWith('.svg'))) {
    // the size of the picture is the size of the SVG
    const svg = fs.readFileSync(path.resolve(folder, name), 'utf8');
    await page.setViewportSize({ width: Number(svg.match(/width="(\d+)"/)[1]), height: Number(svg.match(/height="(\d+)"/)[1]) });
    await page.goto('file://' + path.resolve(folder, name));
    // the logo embeds its font
    await page.evaluate(() => document.fonts && document.fonts.ready);
    // transparent where the SVG draws nothing, e.g. the round corners of the favicon
    await page.screenshot({ path: path.join(folder, name.replace('.svg', '.png')), omitBackground: true });
    console.log('rendered', name);
  }
  await browser.close();
})();
