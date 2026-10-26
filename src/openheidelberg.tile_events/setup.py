from os import path

from setuptools import find_namespace_packages
from setuptools import setup

NAME = 'openheidelberg.tile_events'
DESCRIPTION = 'OpenHeidelberg tile that lists club and association events inside a tiles page.'
VERSION = '0.1.0.dev0'
REQUIRES_PYTHON = '>=3.8'

REQUIRED = [
    'setuptools',
    'Products.CMFPlone>=5.2.2',
    'interaktiv.basetiles',
]
EXTRAS = {
    'test': [
        'plone.app.testing',
    ],
}

this_directory = path.abspath(path.dirname(__file__))

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
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: Addon',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='',
    author='Maik Röder',
    license='GPL',
    packages=find_namespace_packages('src'),
    namespace_packages=['openheidelberg'],
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
    """,
)
