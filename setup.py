#!/usr/bin/env python
"""Installs RunSnakeRun using distutils

Run:
	python setup.py install
to install the package from the source archive.
"""
from setuptools import setup

if __name__ == "__main__":
	extraArguments = {
		'classifiers': [
			"""License :: OSI Approved :: BSD License""",
			"""Programming Language :: Python""",
			"""Topic :: Software Development :: Libraries :: Python Modules""",
			"""Intended Audience :: Developers""",
		],
		'keywords': 'profile,gui,wxPython,squaremap',
		'long_description' : """GUI Viewer for Python profiling runs

Provides explorability and overall visualization of the call tree
and package/module structures.""",
		'platforms': ['Any'],
	}
	### Now the actual set up call
	setup (
		name = "RunSnakeRun",
		version = '2.0.0a1',
		url = "http://www.vrplumber.com/programming/runsnakerun/",
		download_url = "http://www.vrplumber.com/programming/runsnakerun/",
		description = "GUI Viewer for Python profiling runs",
		author = "Mike C. Fletcher",
		author_email = "mcfletch@vrplumber.com",
		license = "BSD",
		package_dir = {
			'runsnakerun':'.',
		},
		packages = [
			'runsnakerun',
		],
		options = {
			'sdist':{'force_manifest':1,'formats':['gztar','zip'],},
		},
		zip_safe=False,
		entry_points = {
			'gui_scripts': [
				'runsnake=runsnakerun.runsnake:main',
			],
		},
		**extraArguments
	)

