"""Checks on the files of the package. They need neither Plone nor an import of the package.

They guard what a rename or a new layout can break unnoticed: names that must agree between setup.py, the ZCML, the
GenericSetup profiles, manifest.cfg and the Diazo rules, and includes that point to files that do not exist.
"""
import configparser
import os
import re
import unittest
import xml.etree.ElementTree as ElementTree

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PACKAGE_DIR, 'static')
SETUP_PY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(PACKAGE_DIR))), 'setup.py')
NAME = 'openheidelberg.theme'
OLD_NAME = 'openheidelberg.' + 'layout'
INTERFACE = 'openheidelberg.theme.interfaces.IOpenHeidelbergThemeLayer'

TEXT_SUFFIXES = ('.py', '.zcml', '.xml', '.cfg', '.html', '.css', '.js', '.svg')


def list_files(directory, suffixes):
    result = []
    for root, dirs, names in os.walk(directory):
        dirs[:] = sorted(dirs)
        if '__pycache__' in root:
            continue
        for name in sorted(names):
            if name.endswith(suffixes):
                result.append(os.path.join(root, name))
    return result


def read_text(path):
    with open(path, encoding='utf-8', newline='') as handle:
        return handle.read()


def local_name(tag):
    return tag.split('}')[-1]


def find_elements(path, name):
    result = []
    for element in ElementTree.parse(path).iter():
        if local_name(element.tag) == name:
            result.append(element)
    return result


class TestWellFormed(unittest.TestCase):

    def test_xml_files_are_well_formed(self):
        files = list_files(PACKAGE_DIR, ('.xml', '.zcml'))
        self.assertTrue(files)
        for path in files:
            try:
                ElementTree.parse(path)
            except ElementTree.ParseError as error:
                self.fail('%s: %s' % (path, error))

    def test_text_files_use_lf_only(self):
        for path in list_files(PACKAGE_DIR, TEXT_SUFFIXES):
            self.assertNotIn('\r', read_text(path), path)

    def test_old_package_name_is_gone(self):
        for path in list_files(PACKAGE_DIR, TEXT_SUFFIXES):
            self.assertNotIn(OLD_NAME, read_text(path), path)
        self.assertNotIn(OLD_NAME, read_text(SETUP_PY))


class TestThemeNames(unittest.TestCase):

    def test_manifest_prefix_and_rules(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(os.path.join(STATIC_DIR, 'manifest.cfg'), encoding='utf-8')
        prefix = parser.get('theme', 'prefix')
        self.assertEqual(prefix, '/++theme++' + NAME)
        self.assertEqual(parser.get('theme', 'rules'), prefix + '/rules.xml')
        self.assertTrue(os.path.isfile(os.path.join(STATIC_DIR, 'rules.xml')))

    def test_manifest_parameters_the_rules_use(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(os.path.join(STATIC_DIR, 'manifest.cfg'), encoding='utf-8')
        self.assertTrue(parser.has_option('theme:parameters', 'site_layout_enabled'))
        self.assertIn('site_layout_enabled', read_text(os.path.join(STATIC_DIR, 'rules.xml')))

    def test_static_resource_directory_is_registered_under_the_package_name(self):
        statics = find_elements(os.path.join(PACKAGE_DIR, 'configure.zcml'), 'static')
        self.assertEqual(len(statics), 1)
        self.assertEqual(statics[0].get('name'), NAME)
        self.assertEqual(statics[0].get('type'), 'theme')
        self.assertEqual(statics[0].get('directory'), 'static')

    def test_profiles_enable_and_restore_the_right_theme(self):
        default = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'default', 'theme.xml'), 'name')
        self.assertEqual(default[0].text.strip(), NAME)
        uninstall = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'uninstall', 'theme.xml'), 'name')
        self.assertEqual(uninstall[0].text.strip(), 'interaktiv.theme')

    def test_browser_layer_in_profile_matches_the_interface(self):
        layers = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'default', 'browserlayer.xml'), 'layer')
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].get('name'), NAME)
        self.assertEqual(layers[0].get('interface'), INTERFACE)
        self.assertIn('class IOpenHeidelbergThemeLayer', read_text(os.path.join(PACKAGE_DIR, 'interfaces.py')))

    def test_uninstall_removes_the_browser_layer(self):
        layers = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'uninstall', 'browserlayer.xml'), 'layer')
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].get('name'), NAME)
        self.assertEqual(layers[0].get('remove'), 'true')

    def test_behavior_name_agrees_in_zcml_and_both_profiles(self):
        behaviors = find_elements(os.path.join(PACKAGE_DIR, 'configure.zcml'), 'behavior')
        self.assertEqual(len(behaviors), 1)
        behavior_name = behaviors[0].get('name')
        self.assertEqual(behavior_name, NAME + '.page_layout')

        install = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'default', 'types', 'TilePage.xml'), 'element')
        self.assertEqual(len(install), 1)
        self.assertEqual(install[0].get('value'), behavior_name)
        self.assertIsNone(install[0].get('remove'))

        uninstall = find_elements(os.path.join(PACKAGE_DIR, 'profiles', 'uninstall', 'types', 'TilePage.xml'), 'element')
        self.assertEqual(len(uninstall), 1)
        self.assertEqual(uninstall[0].get('value'), behavior_name)
        self.assertEqual(uninstall[0].get('remove').lower(), 'true')

    def test_vocabulary_name_agrees_in_zcml_and_schema(self):
        utilities = find_elements(os.path.join(PACKAGE_DIR, 'configure.zcml'), 'utility')
        names = []
        for utility in utilities:
            if utility.get('provides') == 'zope.schema.interfaces.IVocabularyFactory':
                names.append(utility.get('name'))
        self.assertEqual(names, [NAME + '.page_layouts'])
        self.assertIn("vocabulary='%s.page_layouts'" % NAME, read_text(os.path.join(PACKAGE_DIR, 'interfaces.py')))

    def test_body_class_adapter_registration(self):
        adapters = find_elements(os.path.join(PACKAGE_DIR, 'configure.zcml'), 'adapter')
        self.assertEqual(len(adapters), 1)
        adapter = adapters[0]
        self.assertEqual(adapter.get('for'), '* ' + NAME + '.interfaces.IOpenHeidelbergThemeLayer')
        self.assertEqual(adapter.get('factory'), '.body_classes.OpenHeidelbergBodyClasses')
        # the name "layout" belongs to interaktiv.layout; two adapters of one name would conflict
        self.assertEqual(adapter.get('name'), NAME)
        self.assertNotEqual(adapter.get('name'), 'layout')

    def test_setup_py_names_the_package(self):
        text = read_text(SETUP_PY)
        self.assertIn("NAME = '%s'" % NAME, text)
        self.assertIn("namespace_packages=['openheidelberg']", text)


class TestDiazoFiles(unittest.TestCase):

    def test_includes_and_themes_point_to_existing_files(self):
        prefix = '++theme++' + NAME + '/'
        checked = 0
        for path in list_files(STATIC_DIR, ('.xml',)):
            text = read_text(path)
            for href in re.findall(r'href="([^"]+)"', text):
                if not href.startswith('++theme++'):
                    continue
                if not href.startswith(prefix):
                    # a file of another theme, e.g. ++theme++interaktiv.theme/rules.xml
                    continue
                target = os.path.join(STATIC_DIR, href[len(prefix):])
                self.assertTrue(os.path.isfile(target), '%s includes %s' % (path, href))
                checked += 1
        self.assertGreater(checked, 5)

    def test_theme_files_link_existing_local_resources(self):
        checked = 0
        for path in list_files(STATIC_DIR, ('.html',)):
            text = read_text(path)
            for url in re.findall(r'(?:href|src)="([^"]+)"', text):
                if url.startswith(('/', 'http:', 'https:', '#', 'data:', 'mailto:')):
                    continue
                target = os.path.join(STATIC_DIR, url)
                self.assertTrue(os.path.isfile(target), '%s links %s' % (path, url))
                checked += 1
        self.assertGreater(checked, 2)

    def test_every_layout_folder_has_rules(self):
        layouts_dir = os.path.join(STATIC_DIR, 'layouts')
        names = sorted(os.listdir(layouts_dir))
        self.assertIn('site-search-layout', names)
        self.assertIn('site-layout', names)
        self.assertIn('site-edit-layout', names)
        for name in names:
            self.assertTrue(os.path.isfile(os.path.join(layouts_dir, name, 'rules.xml')), name)

    def test_dispatcher_branches(self):
        text = read_text(os.path.join(STATIC_DIR, 'rules.xml'))
        self.assertIn('body.layout-site-search-layout', text)
        self.assertIn('body.edit-mode', text)
        self.assertIn('layouts/site-search-layout/rules.xml', text)
        self.assertIn('layouts/site-layout/rules.xml', text)
        self.assertIn('layouts/site-edit-layout/rules.xml', text)
        self.assertIn('++theme++interaktiv.theme/rules.xml', text)
        # the iframe branch was removed on 2026-11-09 and must not come back unnoticed
        without_comments = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        self.assertNotIn('iframe', without_comments)


if __name__ == '__main__':
    unittest.main()
