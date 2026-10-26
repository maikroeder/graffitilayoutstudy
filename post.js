// fixes conflict with plones require js -> moment/de.js asynchronous integration
// pre.js and post.js
window.define = window.__define;
window.require = window.__require;
window.__define = undefined;
window.__require = undefined;
