// fixes conflict with plones require js -> moment/de.js asynchronous integration
// pre.js and post.js
window.__define = window.define;
window.__require = window.require;
window.define = undefined;
window.require = undefined;
