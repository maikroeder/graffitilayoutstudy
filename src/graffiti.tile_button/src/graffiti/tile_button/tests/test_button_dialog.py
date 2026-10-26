import plone.api as api
from graffiti.tile_button.modals.button_dialog import ButtonDialogContent
from graffiti.tile_button.modals.button_dialog import ButtonDialogTabs
from graffiti.tile_button.settings import ENABLED_RECORD
from graffiti.tile_button.tests.test_css_classes import ButtonTestCase
from interaktiv.tile_button.modals.api.content import ConfigureTileButtonContent
from interaktiv.tile_button.modals.api.tabs import ConfigureTileButtonTabs


class TestButtonDialog(ButtonTestCase):

    def setUp(self):
        super().setUp()
        self.request.form['id'] = self.tile['id']

    def get_tab_ids(self):
        view = api.content.get_view(
            name='configure_tile_button_navigation_tabs', context=self.tilepage, request=self.request)
        return [tab['id'] for tab in view.get_tabs()]

    def get_content(self) -> str:
        view = api.content.get_view(name='configure_tile_button_content', context=self.tilepage, request=self.request)
        return view()

    def switch_off(self):
        api.portal.set_registry_record(ENABLED_RECORD, False)

    def test_views_of_this_package_are_used(self):
        for name, cls in (('configure_tile_button_navigation_tabs', ButtonDialogTabs),
                          ('configure_tile_button_content', ButtonDialogContent)):
            self.assertIsInstance(api.content.get_view(name=name, context=self.tilepage, request=self.request), cls)

    def test_tab_with_style_permission(self):
        self.assertEqual(self.get_tab_ids()[-1], 'css_classes')

    def test_no_tab_without_style_permission(self):
        self.remove_style_permission()
        self.assertNotIn('css_classes', self.get_tab_ids())

    def test_no_tab_when_switched_off(self):
        self.switch_off()
        self.assertNotIn('css_classes', self.get_tab_ids())

    def test_field_inside_the_form(self):
        self.tile['button_css_classes'] = 'open-dialog'
        content = self.get_content()
        self.assertIn('id="tab-css_classes"', content)
        self.assertIn('value="open-dialog"', content)
        # inside the form, so the dialog of the button tile saves it together with the other fields
        self.assertLess(content.index('name="button_css_classes"'), content.rindex('</form>'))

    def test_no_field_without_style_permission(self):
        self.remove_style_permission()
        self.assertNotIn('name="button_css_classes"', self.get_content())

    def test_no_field_when_switched_off(self):
        self.switch_off()
        self.assertNotIn('name="button_css_classes"', self.get_content())

    def test_classes_stay_on_the_button_when_switched_off(self):
        self.tile['button_css_classes'] = 'open-dialog'
        self.switch_off()
        self.assertEqual(self.get_view().get_button_classes(), 'button open-dialog')

    def test_tabs_match_the_original(self):
        """ If this test fails after an update of interaktiv.tile_button, compare modals/button_dialog.py
        with the tabs of the original dialog. """
        original = ConfigureTileButtonTabs(self.tilepage, self.request).get_tabs()
        self.assertEqual(ButtonDialogTabs(self.tilepage, self.request).get_tabs()[:-1], original)

    def test_content_matches_the_original(self):
        """ If this test fails after an update of interaktiv.tile_button, check where the pane of the
        new tab is inserted in modals/button_dialog.py. """
        original = ConfigureTileButtonContent(self.tilepage, self.request)()
        view = ButtonDialogContent(self.tilepage, self.request)
        own = view()
        self.assertIn('</form>', original)
        self.assertEqual(own.replace(view.css_classes_pane(view), ''), original)
