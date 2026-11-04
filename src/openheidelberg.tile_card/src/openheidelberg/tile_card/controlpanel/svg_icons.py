from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from openheidelberg.tile_card import _
from openheidelberg.tile_card.controlpanel.usage import find_svg_icon_usage
from openheidelberg.tile_card.svg_sanitizer import SvgError
from openheidelberg.tile_card.svg_sanitizer import check_name
from openheidelberg.tile_card.svg_sanitizer import sanitize_svg
from openheidelberg.tile_card.vocabularies.svg_icons import get_bundled_svg_icons
from openheidelberg.tile_card.vocabularies.svg_icons import get_svg_icons
from openheidelberg.tile_card.vocabularies.svg_icons import set_svg_icons
from plone.protect.authenticator import createToken
from plone.protect.authenticator import check as check_token
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import Forbidden


class SvgIconsControlPanel(BrowserView):
    """Control panel "Card tile SVG icons": the svg icons the editors can choose in the card tile.

    Actions (POST, with the authenticator token): add or replace an icon (pasted markup or an uploaded .svg file),
    delete an icon, add the bundled icons that are missing. Markup is sanitised before it is stored.
    """

    template = ViewPageTemplateFile('templates/svg_icons.pt')

    def __call__(self) -> str:
        self.errors = []
        self.form_name = ''
        self.form_svg = ''
        if self.request.get('REQUEST_METHOD') == 'POST':
            if not check_token(self.request):
                raise Forbidden('Invalid authenticator token')
            self.handle_post()
        return self.template()

    def authenticator_token(self) -> str:
        return createToken()

    def get_usage(self) -> dict:
        """Icon name -> pages that use it; read once per request."""
        if not hasattr(self, '_usage'):
            self._usage = find_svg_icon_usage(self.context)
        return self._usage

    def get_icons(self) -> list:
        usage = self.get_usage()
        result = []
        for name, markup in get_svg_icons().items():
            result.append({'name': name, 'svg': markup, 'used_on': usage.get(name, [])})
        return result

    def get_missing_bundled(self) -> list:
        stored = get_svg_icons()
        missing = []
        for name in get_bundled_svg_icons():
            if name not in stored:
                missing.append(name)
        return missing

    def message(self, text: str, kind: str = 'info') -> None:
        IStatusMessage(self.request).add(text, type=kind)

    def handle_post(self) -> None:
        form = self.request.form
        if form.get('form.button.delete'):
            self.delete(form.get('name', ''))
        elif form.get('form.button.restore'):
            self.restore_bundled()
        elif form.get('form.button.add'):
            self.add(form)

    def add(self, form: dict) -> None:
        self.form_name = (form.get('name', '') or '').strip()
        markup = form.get('svg', '') or ''
        upload = form.get('svg_file', None)
        if upload is not None and getattr(upload, 'filename', ''):
            raw = upload.read()
            try:
                markup = raw.decode('utf-8')
            except UnicodeDecodeError:
                self.errors.append('The file is not UTF-8 text.')
                return
            if not self.form_name:
                base = upload.filename.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
                self.form_name = base[:-4] if base.lower().endswith('.svg') else base
                self.form_name = self.form_name.lower().replace(' ', '-')
        self.form_svg = markup
        try:
            name = check_name(self.form_name)
            cleaned = sanitize_svg(markup)
        except SvgError as error:
            self.errors.append(str(error))
            return
        icons = get_svg_icons()
        replaced = name in icons
        icons[name] = cleaned
        set_svg_icons(icons)
        self.form_name = ''
        self.form_svg = ''
        self.message(_('Icon "${name}" saved.', mapping={'name': name}) if not replaced else
                     _('Icon "${name}" replaced.', mapping={'name': name}))

    def delete(self, name: str) -> None:
        icons = get_svg_icons()
        if name not in icons:
            return
        used_on = self.get_usage().get(name, [])
        if used_on:
            # the template disables the button; this is the check that counts
            self.message(_('Icon "${name}" is used by ${count} page(s) and can not be deleted.',
                           mapping={'name': name, 'count': str(len(used_on))}), 'error')
            return
        del icons[name]
        set_svg_icons(icons)
        self.message(_('Icon "${name}" deleted. Cards that use it show no vector icon.', mapping={'name': name}))

    def restore_bundled(self) -> None:
        icons = get_svg_icons()
        added = []
        for name, markup in get_bundled_svg_icons().items():
            if name not in icons:
                icons[name] = sanitize_svg(markup)
                added.append(name)
        set_svg_icons(icons)
        self.message(_('Added: ${names}', mapping={'names': ', '.join(added) or '-'}))
