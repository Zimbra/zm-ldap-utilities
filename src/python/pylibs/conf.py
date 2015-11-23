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


import os

class Config:
	def __init__(self):
		self.config = {}
		self.progname 	= "zmconfigd"
		if (os.getenv("zimbra_server_hostname") is not None):
			self.hostname 	= os.getenv("zimbra_server_hostname")
		else:
			self.hostname 	= os.popen("/opt/zimbra/bin/zmhostname").readline().strip()
		if (self.hostname is None or self.hostname == ""):
			os._exit(1)
		self.wd_all 	= False
		self.debug 		= False
		self.baseDir	= "/opt/zimbra"
		self.logStatus 	= { 
						4 : "Debug", 
						3 : "Info", 
						2 : "Warning", 
						1 : "Error", 
						0 : "Fatal"
						}
		self.configFile = self.baseDir+"/conf/zmconfigd.cf";
		self.logFile    = self.baseDir+"/log/"+self.progname+".log";
		self.pidFile    = self.baseDir+"/log/"+self.progname+".pid";
		self.interval 	= 60
		if self.debug:
			self.interval  = 10
		self.restartconfig = False
		self.watchdog 	= True
		self.wd_list	= [ "antivirus" ]
		self.loglevel 	= 3

	def __setitem__(self, key, val):
		self.config[key] = val

	def __getitem__(self, key):
		try:
			return self.config[key]
		except Exception, e:
			return None

	def setVals(self, state):
		self.ldap_is_master = state.localconfig["ldap_is_master"]
		self.ldap_root_password = state.localconfig["ldap_root_password"]
		self.ldap_master_url = state.localconfig["ldap_master_url"]
		self.loglevel 	= 3
		if state.localconfig["ldap_starttls_required"] is not None:
			self.ldap_starttls_required = (state.localconfig["ldap_starttls_required"].upper() != "FALSE")
		if state.localconfig["zmconfigd_log_level"] is not None:
			self.loglevel 	= int(state.localconfig["zmconfigd_log_level"])
		self.interval 	= 60
		if state.localconfig["zmconfigd_interval"] is not None and state.localconfig["zmconfigd_interval"] != "":
			self.interval 	= int(state.localconfig["zmconfigd_interval"])
		self.debug 		= False
		if state.localconfig["zmconfigd_debug"] is not None:
			self.debug 		= state.localconfig["zmconfigd_debug"]
		if state.localconfig["zmconfigd_watchdog"] is not None:
			self.watchdog	= (state.localconfig["zmconfigd_watchdog"].upper() != "FALSE")
		if state.localconfig["zmconfigd_enable_config_restarts"] is not None:
			self.restartconfig = (state.localconfig["zmconfigd_enable_config_restarts"].upper() != "FALSE")
		if state.localconfig["zmconfigd_watchdog_services"] is not None:
			self.wd_list = state.localconfig["zmconfigd_watchdog_services"].split()
