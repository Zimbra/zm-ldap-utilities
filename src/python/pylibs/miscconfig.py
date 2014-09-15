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
import commands
import config
import re
import threading
import time

class MiscConfig(config.Config):
	def load(self):
		self.loaded = True

		t1 = time.clock()
		#th = []
		for cm in commands.miscCommands:
			self.doCommand(cm);
			#th.append(threading.Thread(target=MiscConfig.doCommand,args=(self,cm),name=cm))
		
		#[t.setDaemon(True) for t in th]
		#[t.start() for t in th]
		#[t.join(60) for t in th]
		dt = time.clock()-t1
		Log.logMsg(5,"Miscconfig loaded in %.2f seconds" % dt)


	def doCommand(self, cm):
		c = commands.commands[cm]
		rc = c.execute();
		if (rc != 0):
			Log.logMsg(1, "Skipping "+c.desc+" update.");
			Log.logMsg(1, str(c));
			return None

		# lines = c.output.splitlines()

		# if no output was returned we have a potential avoid stopping all services
		if (len(c.output) == 0):
			Log.logMsg(2, "Skipping " + c.desc + " No data returned.")
			c.status = 1
			return

		self[c.name] = ' '.join(c.output)
		Log.logMsg(5, "%s=%s" % (c.name, self[c.name]));
		# v = ' '.join(lines)
		# self[cm] = self[cm] and (self[cm] + " " + v) or v

