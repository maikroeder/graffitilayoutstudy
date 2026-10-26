from os import path

from setuptools import find_namespace_packages, setup

# Package metadata
NAME = 'graffiti.tile_button'
DESCRIPTION = 'Custom CSS classes for the button tile of interaktiv.tile_button.'
URL = 'https://code.interaktiv.de/interaktiv/graffiti/'
EMAIL = 'support@interaktiv.de'
AUTHOR = 'Interaktiv GmbH'
REQUIRES_PYTHON = '>=3.8'
VERSION = '1.0.0'
REQUIRES_PLONE_VERSION = '5.2.2'

# Additional package requires
REQUIRED = [
    'setuptools',
    'Products.CMFPlone>=' + REQUIRES_PLONE_VERSION,
    'interaktiv.basetiles',
    'interaktiv.tile_button'
]
EXTRAS = {
    'test': [
        'plone.app.testing'
    ]
}

this_directory = path.abspath(path.dirname(__file__))

# Load long description from README.md
try:
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

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
    packages=find_namespace_packages('src'),
    # needed by z3c.autoinclude on Plone 5.2 to find the package inside the namespace
    namespace_packages=['graffiti'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
