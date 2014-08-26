#
# ***** BEGIN LICENSE BLOCK *****
# Zimbra Collaboration Suite Server
# Copyright (C) 2010, 2012, 2013, 2014 Zimbra, Inc.
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# version 2 of the License.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****
#


from logmsg import *

class Config:
	def __init__(self):
		self.loaded = False
		self.config = {}
		self.serviceconfig = {}

	def __setitem__(self,key,val):
		self.config[key] = val
		return self.config[key]

	def __getitem__(self,key):
		if key in self.config:
			val = self.config[key]
			if isinstance (val, basestring):
				return val
			else:
				return " ".join(val)
		else:
			return None

	def __contains__(self,key):
		return key in self.config

	def load(self):
		self.loaded = True
		self.config = {}

	def dump(self):
		for k in sorted(self.config.iterkeys()):
			print "%s = %s" % (k, self[k])
