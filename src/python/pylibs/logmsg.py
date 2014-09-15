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

import os
import conf
import sys
import logging
import time
import logging
import logging.handlers
import re
import threading

from org.productivity.java.syslog4j import Syslog
from org.productivity.java.syslog4j import SyslogIF
from org.productivity.java.syslog4j import SyslogConstants
from org.productivity.java.syslog4j.impl.unix import UnixSyslog
from org.productivity.java.syslog4j.impl.unix.socket import UnixSocketSyslogConfig

class Log:
	zmconfigdSyslogInstance = UnixSocketSyslogConfig(SyslogConstants.FACILITY_LOCAL0, "/dev/log")
	zmsyslog = Syslog.createInstance("zmSyslog",zmconfigdSyslogInstance)
	zmsyslog.getConfig().setLocalName("zmconfigd[%d]:" % os.getpid())

	@classmethod
	def initLogging(cls, c = None):
		if c:
			cls.cf = c
			if cls.cf.loglevel > 5:
				cls.cf.loglevel = 5
		else:
			cls.cf = conf.Config()

	@classmethod
	def logMsg(cls, lvl, msg):

		if lvl > 5:
			lvl = 5
		msg = re.sub(r"\s|\n", " ", msg)

		if lvl <= cls.cf.loglevel:
			Log.zmsyslog.log(lvl, msg)

		if lvl == 0:
			Log.zmsyslog.log(2, "%s: shutting down" % (cls.cf.progname,) )
			os._exit(1)

Log.initLogging()
