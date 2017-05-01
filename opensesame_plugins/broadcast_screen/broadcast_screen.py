#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.item import item
from libopensesame.exceptions import osexception
from libqtopensesame.items.qtautoplugin import qtautoplugin
import os
import sys
import imp

class broadcast_screen(item):

	"""
	desc:
		A plug-in that sends the OpenSesame display to external devices.
	"""

	description = u'Broadcast the screen to external devices'

	def reset(self):

		"""
		desc:
			Resets plug-in to initial values.
		"""

		self.var.screens = u'localhost 0 0 [width] [height] 0 50008'
		self.var.display_mode = u'Enable main display'

	def prepare(self):

		"""
		desc:
			Initialize all external screens.
		"""

		item.prepare(self)
		# Check that we're using the legacy back-end
		if self.var.canvas_backend != u'legacy':
			raise osexception(u'broadcast_screen requires the legacy backend')
		# Load the broadcast canvas backend
		mod = imp.load_source(u'broadcast',
			os.path.join(os.path.dirname(__file__), 'broadcast_canvas.py'))
		sys.modules[u'openexp._canvas.broadcast'] = mod
		mod.set_display_mode(self.var.display_mode)
		self.experiment.set(u'canvas_backend', u'broadcast')
		# Parse all screens
		for line in self.var.screens.split(u'\n'):
			l = line.strip().split()
			if len(l) == 0 or line.startswith(u'#'):
				continue
			try:
				assert(len(l) == 7)
				x = int(l[1])
				y = int(l[2])
				w = int(l[3])
				h = int(l[4])
				rot = int(l[5])
				port = int(l[6])
			except:
				raise osexception(u'Failed to parse screens specification')
			mod.add_screen(l[0], x, y, w, h, rot, port)

class qtbroadcast_screen(broadcast_screen, qtautoplugin):

	def __init__(self, name, experiment, script=None):

		broadcast_screen.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)
