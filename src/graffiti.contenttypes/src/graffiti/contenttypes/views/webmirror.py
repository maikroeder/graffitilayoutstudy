import mimetypes
import os
from typing import Union, List
from urllib.parse import urlparse

import lxml.html
from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from lxml.html import HtmlElement


class WebMirrorView(BrowserView):
    """Render a local HTML file inside Plone."""

    template = ViewPageTemplateFile("templates/webmirror/view.pt")

    def __call__(self) -> str:
        return self.template(self)

    def _make_links_absolute(self, node: HtmlElement) -> HtmlElement:
        """
        Converts all relative <a href> links to absolute URLs based on the context's URL.

        Skips:
        - Anchor links (#)
        - External URLs (containing a netloc)
        - Special case: '../some-id' gets converted to '../../some-id/'
        """
        context_url = self.context.absolute_url()

        for tag in node.xpath('//*[@href]'):
            href = tag.attrib['href']

            if href == '#':
                continue  # Skip anchor links

            if bool(urlparse(href).netloc):
                continue  # Skip external links

            # if href.startswith('../'):
            #     # Heuristic: '../object-id/foo.html' → '../../object-id/foo.html'
            #     content_id = href.split('/')[1]
            #     href = href.replace('../', f'../../{content_id}/', 1)

            tag.attrib['href'] = context_url + '/' + href

        return node

    def _make_sources_absolute(self, node: HtmlElement) -> HtmlElement:
        """
        Converts relative image/video/audio <src> paths to absolute URLs.

        Specifically replaces '../images' with the context's '/assets' path.
        """
        for tag in node.xpath('//*[@src]'):
            src = tag.attrib['src']
            if './' in src:
                tag.attrib['src'] = src.replace(
                    './images',
                    self.context.absolute_url() + '/assets'
                )
        return node

    @staticmethod
    def _get_html_body(html_code: Union[str, bytes]) -> HtmlElement:
        """
        Extracts the <body> element from a full HTML document.

        Args:
            html_code: HTML content as a string or bytes.

        Returns:
            The <body> tag as an HtmlElement.

        Raises:
            ValueError: If no <body> tag is found.
        """
        html_node = lxml.html.fromstring(html_code)
        body = html_node.find('body')
        if body is None:
            raise ValueError("No <body> element found in the HTML")
        return body

    def _get_path(self) -> str:
        """
        Determines the path to the local HTML file to render.

        If a `webmirror_path` parameter is provided in the request, it's appended.
        Otherwise, defaults to 'index.html'.
        """
        path = self.context.get_webmirror()
        request_path = self.request.get('webmirror_path', '')
        if request_path:
            path += '/' + request_path
        else:
            path += '/index.html'
        return path

    def postprocess_html(self, node: HtmlElement) -> HtmlElement:
        """
        Applies postprocessing to the parsed HTML <body>:
        - Makes links absolute
        - Makes image/video sources absolute
        """
        node = self._make_links_absolute(node)
        node = self._make_sources_absolute(node)
        return node

    def get_html(self) -> str:
        """
        Loads and parses a local HTML file, extracts and returns its processed <body> content.

        Returns:
            A string containing the inner HTML of the <body> tag (excluding the <body> tag itself).
            Returns an empty string if the file does not exist.
        """
        file_path = self._get_path()
        if not os.path.exists(file_path):
            return ''

        with open(file_path, 'rb') as file_handler:
            body_node = self._get_html_body(file_handler.read())

        body_node = self.postprocess_html(body_node)

        # Extract only the children of <body>, not the <body> tag itself
        content_nodes: List[HtmlElement] = body_node.getchildren()
        content_str = ''.join(
            lxml.html.tostring(child, encoding='unicode')
            for child in content_nodes
        )
        return content_str

class WebmirrorAssetView(WebMirrorView):

    @staticmethod
    def is_subdir(path: str, directories: Union[str, List]) -> bool:
        is_subpath = False
        if isinstance(directories, str):
            directories = [directories]
        for directory in directories:
            directory = os.path.join(os.path.realpath(directory), '')
            path = os.path.realpath(path)
            if os.path.commonprefix([path, directory]) == directory:
                is_subpath = True
        return is_subpath

    def __call__(self):
        return self.fetch_file(replace_what="assets", with_what="./images")

    def fetch_file(self, replace_what: str, with_what: str) -> bytes:
        path = self._get_path()
        content_type, content_encoding = mimetypes.guess_type(path)
        request = getattr(self, 'request', None)
        if content_type:
            request.response.setHeader('Content-Type', content_type)
        if content_encoding is not None:
            request.response.setHeader('Content-Encoding', content_encoding)
        # XXX Assumes the string does not appear anywhere else in the path
        path = path.replace(replace_what, with_what)

        if not self.is_subdir(path, self.context._get_base_path()):
            raise Unauthorized('Invalid path')

        with open(path, 'rb') as file_handler:
            file_content = file_handler.read()
        return file_content