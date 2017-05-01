#!/usr/bin/env python
# coding=utf-8

"""
This file is part of broadcast_screen.

broadcast_screen is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

broadcast_screen is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with broadcast_screen.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

setup(
	name='opensesame-plugin-broadcast_screen',
	version='0.2.1',
	description='Screen broadcast plugin for OpenSesame',
	author='Sebastiaan Mathot',
	author_email='s.mathot@cogsci.nl',
	url='https://github.com/smathot/opensesame-plugin-broadcast_screen',
	# Classifiers used by PyPi if you upload the plugin there
	classifiers=[
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Environment :: MacOS X',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 2',
	],
	data_files=[
		('share/opensesame_plugins/broadcast_screen',
		[
			'opensesame_plugins/broadcast_screen/broadcast_screen.png',
			'opensesame_plugins/broadcast_screen/broadcast_screen_large.png',
			'opensesame_plugins/broadcast_screen/broadcast_screen.py',
			'opensesame_plugins/broadcast_screen/broadcast_canvas.py',
			'opensesame_plugins/broadcast_screen/info.yaml',
			]
		),
		]
	)
