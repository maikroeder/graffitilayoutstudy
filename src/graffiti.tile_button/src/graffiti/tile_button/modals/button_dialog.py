""" Tab "CSS classes" in the dialog of the button tile.

Nothing of the dialog of interaktiv.tile_button is copied: the tabs get one more entry, and the pane of the
new tab is inserted into the rendered dialog right before the closing form tag. The dialog saves all fields of
its form through update_content, so the new field is saved with the others. tests/test_button_dialog.py
compares the result with the original dialog, a change of the original after an update shows up there.
"""
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_button.settings import offer_css_classes
from interaktiv.tile_button.modals.api.content import ConfigureTileButtonContent
from interaktiv.tile_button.modals.api.tabs import ConfigureTileButtonTabs

TAB_ID = 'css_classes'
FORM_END = '</form>'


class ButtonDialogTabs(ConfigureTileButtonTabs):

    def get_tabs(self):
        tabs = super().get_tabs()
        if offer_css_classes(self.context):
            tabs.append({'id': TAB_ID, 'css_class': TAB_ID})
        return tabs


class ButtonDialogContent(ConfigureTileButtonContent):
    css_classes_pane = ViewPageTemplateFile('templates/css_classes_tab.pt')

    def __call__(self):
        html = super().__call__()
        if not html or not offer_css_classes(self.context):
            return html
        position = html.rfind(FORM_END)
        if position == -1:
            # the dialog of the button tile changed, see the module docstring
            return html
        return html[:position] + self.css_classes_pane(self) + html[position:]
