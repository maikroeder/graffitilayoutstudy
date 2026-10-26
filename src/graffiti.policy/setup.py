import sys
from os import path

from pkg_resources import Requirement, parse_version
from setuptools import find_packages, setup

# Package metadata
NAME = 'graffiti.policy'
DESCRIPTION = ''
URL = 'https://code.interaktiv.de/interaktiv/graffiti/'
EMAIL = 'support@interaktiv.de'
AUTHOR = 'Interaktiv GmbH'
REQUIRES_PYTHON = '~=3.8'
VERSION = '1.0.1'
REQUIRES_PLONE_VERSION = '5.2.2'

# Additional package requires
REQUIRED = [
    'graffiti.contenttypes',
    'graffiti.tile_listing',
    'graffiti.tile_search',
    'graffiti.tile_dashboard',
    'graffiti.tile_tabs',
    'graffiti.tile_view',
    'graffiti.tile_button',
    'graffiti.pdfcheck',

    'setuptools',
    'Products.CMFPlone>=' + REQUIRES_PLONE_VERSION,
    'requests',
    'plone.app.caching',
    'plone.app.contenttypes',
    'collective.solr',

    # Interaktiv
    'interaktiv.framework',
    'interaktiv.layout',
    'interaktiv.fonts',
    'interaktiv.migrator',
    'interaktiv.image_focus',
    'interaktiv.buildinfo',
    'interaktiv.workingcopy',
    # Interaktiv Tiles
    'interaktiv.basetiles',
    'interaktiv.tile_audio',
    'interaktiv.tile_breadcrumbs',
    'interaktiv.tile_button',
    'interaktiv.tile_collapse',
    'interaktiv.tile_contact',
    'interaktiv.tile_files',
    'interaktiv.tile_forms',
    'interaktiv.tile_icon',
    'interaktiv.tile_iframe',
    'interaktiv.tile_image',
    'interaktiv.tile_line',
    'interaktiv.tile_map',
    'interaktiv.tile_news',
    'interaktiv.tile_slider',
    'interaktiv.tile_spacer',
    'interaktiv.tile_subheadline',
    'interaktiv.tile_text',
    'interaktiv.tile_timeline',
    'interaktiv.tile_video',
    'interaktiv.tilepage_versioning',
    'interaktiv.theme',
]
EXTRAS = {
    'test': [
        'plone.app.testing',
        'lxml',
        'requests'
    ]
}

this_directory = path.abspath(path.dirname(__file__))

# Load long description from README.md
try:
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


# Check required python version
def check_python_version():
    required_python = Requirement.parse('python' + REQUIRES_PYTHON)
    current_version = parse_version(".".join(map(str, sys.version_info[:3])))
    if current_version not in required_python:
        sys.exit(f"'{NAME}' requires Python {REQUIRES_PYTHON} but the current Python is {current_version}")


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license='BSD-3-Clause',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['graffiti', ],
    include_package_data=True,
    zip_safe=False,
    python_requires=check_python_version(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
