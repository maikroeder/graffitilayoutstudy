from setuptools import setup, find_packages

version = '1.0'

setup(name='interaktiv.workingcopy',
      version=version,
      description="",
      long_description="",
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='BSD-3-Clause',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['interaktiv', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.behavior',
          'plone.browserlayer',
          'plone.app.iterate',
          'plone.app.content',
          'collective.dexteritydiff'
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'unittest2',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
