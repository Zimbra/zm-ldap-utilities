#
# ***** BEGIN LICENSE BLOCK *****
# Zimbra Collaboration Suite Server
# Copyright (C) 2010, 2011, 2012, 2013, 2014 Zimbra, Inc.
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
import time

class LocalConfig(config.Config):
	def load(self):
		self.loaded = True

		t1 = time.clock()
		c = commands.commands["localconfig"]
		rc = c.execute();
		if (rc != 0):
			Log.logMsg(1, "Skipping "+c.desc+" update.");
			Log.logMsg(1, str(c));
			return None
		dt = time.clock()-t1
		Log.logMsg(5,"Localconfig fetched in %.2f seconds (%d entries)" % (dt,len(c.output)))

		if (len(c.output) == 0):
			Log.logMsg(2, "Skipping " + c.desc + " No data returned.")
			c.status = 1
			raise Exception, "Skipping " + c.desc + " No data returned."

		self.config = dict([(k,v) for (k,v) in c.output])

		# Set a default for this
		if self["zmconfigd_listen_port"] is None:
			self["zmconfigd_listen_port"] = "7171"

		if self["ldap_url"] is not None:
			v = self["ldap_url"]
			v = str(v)
			self["opendkim_signingtable_uri"] = ' '.join([''.join((val,'/?DKIMSelector?sub?(DKIMIdentity=$d)')) for val in self["ldap_url"].split()])
			self["opendkim_keytable_uri"] = ' '.join([''.join((val,'/?DKIMDomain,DKIMSelector,DKIMKey,?sub?(DKIMSelector=$d)')) for val in self["ldap_url"].split()])
			
		dt = time.clock()-t1
		Log.logMsg(5,"Localconfig loaded in %.2f seconds" % dt)
