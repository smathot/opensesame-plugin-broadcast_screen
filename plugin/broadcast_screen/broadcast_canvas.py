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

from openexp._canvas import legacy
from libopensesame.exceptions import osexception
from libopensesame import debug
import random
import pygame
import socket
import json
import base64
import time
import zlib
import threading

screens = []
display_mode = 0
_id = 0
t00 = time.time()

class broadcast(legacy.legacy):

	"""
	desc:
		A custom backend that extends the legacy backend with broadcasting
		functionality.
	"""

	def __init__(self, *args, **kwargs):

		"""See openexp._canvas.canvas"""

		global _id
		legacy.legacy.__init__(self, *args, **kwargs)
		self.prepared = False
		self.id = _id
		print self.experiment.get(u'background')
		self.fill_color = self.color(self.experiment.get(u'background'))
		_id += 1

	def prepare(self):

		"""See openexp._canvas.canvas"""

		self.threads = []
		for screen in screens:
			screen.prepare(self)
			t = threading.Thread(target=screen.show, args=(self,))
			self.threads.append(t)
		random.shuffle(screens)
		# Disable main display
		if display_mode == 1:
			self.surface.fill(self.fill_color)
		# Cut out broadcasted parts
		elif display_mode == 2:
			for screen in screens:
				self.surface.fill(self.fill_color, screen.rect())
		self.prepared = True
		return legacy.legacy.prepare(self)

	def show(self):

		"""See openexp._canvas.canvas"""

		if not self.prepared:
			self.prepare()
		for t in self.threads:
			t.start()
		self.prepared = False
		return legacy.legacy.show(self)

class screen(object):

	"""
	desc:
		A virtual screen that connects to an external device.
	"""

	def __init__(self, host, x, y, w, h, rot=0, port=50008):

		"""
		desc:
			Constructor.

		arguments:
			host:
				desc:	A host name or IP address.
				type:	[str, unicode]
			x:
				desc:	Left edge of the broadcast area.
				type:	int
			y:
				desc:	Top edge of the broadcast area.
				type:	int
			w:
				desc:	Width of the broadcast area.
				type:	int
			h:
				desc:	Height of the broadcast area.
				type:	int

		keywords:
			rot:
				desc:	Counterclockwise rotation of the screen in degrees.
				type:	int
			port:
				desc:	Port number of the host.
				type:	int
		"""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, port))
		self.id = len(screens)
		debug.msg('screen #%s connected %s:%s (%d,%dx%d,%d)' % (self.id,
			host, port, x, y, w, h))
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.rot = rot

	def rect(self):

		"""
		returns:
			desc:	The broadcast area as an (x, y, w, h) tuple.
			type:	tuple
		"""

		return self.x, self.y, self.w, self.h

	def prepare(self, canvas):

		"""
		desc:
			Prepares a canvas for presentation by sending it to the remote
			listener.

		arguments:
			canvas:
				desc:	The canvas to be prepared.
				type:	broadcast
		"""

		debug.msg('prepare #%s on #%s' % (canvas.id, self.id))
		_surface = canvas.surface.subsurface(
			pygame.Rect(self.x, self.y, self.w, self.h))
		if self.rot != 0:
			_surface = pygame.transform.rotate(_surface, self.rot)
			w, h = _surface.get_size()
		else:
			w = self.w
			h = self.h
		data = pygame.image.tostring(_surface, 'RGB')
		data = zlib.compress(data)
		data = base64.b64encode(data)
		d = {
			'cmd'			: 'prepare',
			'id'			: canvas.id,
			'w'				: w,
			'h'				: h,
			'data'			: data,
			'mode'			: 'RGB',
			'compress'		: 'gzip',
			'background'	: canvas.experiment.get(u'background')
			}
		self.send(d)

	def show(self, canvas):

		"""
		desc:
			Shows a previously prepared canvas on the remote listener.

		arguments:
			canvas:
				desc:	The canvas to be shown.
				type:	broadcast
		"""

		debug.msg('show #%s on #%s' % (canvas.id, self.id))
		d = {
			'cmd'	: 'show',
			'id'	: canvas.id
			}
		self.send(d)

	def close(self):

		"""
		desc:
			Closes the connection to the remote listener.
		"""

		debug.msg('close #%s' % self.id)
		d = { 'cmd'	: 'close' }
		self.send(d)
		self.sock.close()

	def send(self, d):

		"""
		desc:
			Sends a command to the remote listener.

		arguments:
			d:
				desc:	A dictionary with command information.
				type:	dict
		"""

		msg = json.dumps(d)
		t0 = time.time()
		self.sock.sendall('%d:%s' % (len(msg), msg))
		data = self.sock.recv(2)
		if data != 'ok':
			raise osexception('Connection error!')
		t1 = time.time()
		print('[%d] sent %d bytes to #%s in %d ms' % (1000.*(t1-t00),
			len(msg), self.id, 1000.*(t1-t0)))

def add_screen(*args, **kwargs):

	"""
	desc:
		Adds a remote screen. See `screen.__init__()` for arguments.
	"""

	screens.append(screen(*args, **kwargs))

def close_display(exp):

	"""
	desc:
		Closes the display and all remote screens.
	"""

	for screen in screens:
		screen.close()
	legacy.close_display(exp)

def set_display_mode(mode):

	"""
	desc:
		Sets the display mode, which determines what should be shown on the main
		display mode.

	arguments:
		mode:
			desc:	A string with the display mode.
			type:	[str, unicode]
	"""

	global display_mode
	if mode == u'Enable main display':
		display_mode = 0
	elif mode == u'Disable main display':
		display_mode = 1
	elif mode == u'Disable broadcasted parts of main display':
		display_mode = 2
	else:
		raise osexception(u'Invalid display mode: %s' % mode)
