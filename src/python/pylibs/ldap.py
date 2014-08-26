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

import conf

from com.zimbra.cs.ldap.LdapServerConfig import GenericLdapConfig
from com.zimbra.cs.ldap import LdapClient
from com.zimbra.cs.ldap import LdapUsage
from com.zimbra.cs.ldap import ZAttributes
from com.zimbra.cs.ldap import ZLdapContext
from com.zimbra.cs.ldap import ZLdapFilter
from com.zimbra.cs.ldap import ZLdapFilterFactory
from com.zimbra.cs.ldap.ZLdapFilterFactory import FilterId
from com.zimbra.cs.ldap import ZSearchControls
from com.zimbra.cs.ldap import ZSearchResultEntry;
from com.zimbra.cs.ldap import ZMutableEntry
from com.zimbra.cs.ldap import ZSearchResultEnumeration
from com.zimbra.cs.ldap import ZSearchScope
from com.zimbra.cs.ldap.LdapException import LdapSizeLimitExceededException
from logmsg import *

# (Key, DN, requires_master)
keymap = {
	"ldap_common_loglevel"			:	("olcLogLevel",		"cn=config", False),
	"ldap_common_threads"			:	("olcThreads",		"cn=config", False),
	"ldap_common_toolthreads"		:	("olcToolThreads",	"cn=config", False),
	"ldap_common_require_tls"		:	("olcSecurity",		"cn=config", False),
	"ldap_common_writetimeout"		:	("olcWriteTimeout",	"cn=config", False),

	"ldap_db_maxsize"			:	("olcDbMaxsize",	"olcDatabase={3}mdb,cn=config", False),
	"ldap_db_envflags"			:	("olcDbEnvFlags",	"olcDatabase={3}mdb,cn=config", False),

	"ldap_accesslog_maxsize"		:	("olcDbMaxsize",	"olcDatabase={2}mdb,cn=config", True),
	"ldap_accesslog_envflags"		:	("olcDbEnvFlags",	"olcDatabase={2}mdb,cn=config", True),

	"ldap_overlay_syncprov_checkpoint"	:	("olcSpCheckpoint",	"olcOverlay={0}syncprov,olcDatabase={3}mdb,cn=config", True),

	"ldap_overlay_accesslog_logpurge"	:	("olcAccessLogPurge",	"olcOverlay={1}accesslog,olcDatabase={3}mdb,cn=config", True)
}

class Ldap:

	master = False
	mLdapConfig = None

	@classmethod
	def initLdap(cls, c = None):
		if c:
			cls.cf = c
			Log.logMsg(5, "Creating ldap context")
			ldapUrl = "ldapi:///"
			bindDN = "cn=config"
			try:
				cls.mLdapConfig =  GenericLdapConfig(ldapUrl, cls.cf.ldap_starttls_required, bindDN, cls.cf.ldap_root_password)
			except Exception, e:
				Log.logMsg(1, "LDAP CONFIG FAILURE (%s)" % e)

		else:
			cls.cf = conf.Config()

	@classmethod
	def modify_attribute(cls, key, value):
		if cls.cf.ldap_is_master:
			atbase = "cn=accesslog"
			atfilter = "(objectClass=*)"
			atreturn = ['1.1']
			zfilter = ZLdapFilterFactory.getInstance().fromFilterString(FilterId.ZMCONFIGD, atfilter)
			searchControls = ZSearchControls.createSearchControls(ZSearchScope.SEARCH_SCOPE_BASE, ZSearchControls.SIZE_UNLIMITED, atreturn)
			mLdapContext = LdapClient.getContext(cls.mLdapConfig, LdapUsage.SEARCH)
			try:
				ne = mLdapContext.searchDir(atbase, zfilter, searchControls)
			except:
				cls.master = False
			else:
				cls.master = True
				Log.logMsg(5, "Ldap config is master")
			LdapClient.closeContext(mLdapContext)
		(attr, dn, xform) = Ldap.lookupKey(key)
		if attr is not None:
			v = xform % (value,)
			atreturn = [attr]
			searchControls = ZSearchControls.createSearchControls(ZSearchScope.SEARCH_SCOPE_BASE, ZSearchControls.SIZE_UNLIMITED, atreturn)
			mLdapContext = LdapClient.getContext(cls.mLdapConfig, LdapUsage.SEARCH)
			ne = mLdapContext.searchDir(dn, zfilter, searchControls)
			entry = ne.next()
			entryAttrs = entry.getAttributes()
			origValue = entryAttrs.getAttrString(attr)
			LdapClient.closeContext(mLdapContext)
			if origValue != v:
				Log.logMsg(4, "Setting %s to %s" % (key, v))
				mLdapContext = LdapClient.getContext(cls.mLdapConfig, LdapUsage.MOD)
				mEntry = LdapClient.createMutableEntry()
				mEntry.setAttr(attr, v)
				try:
					mLdapContext.replaceAttributes(dn, mEntry.getAttributes())
					LdapClient.closeContext(mLdapContext)
				except:
					return 1;

	@classmethod
	def lookupKey(cls, key):
		if key in keymap:
			(attr, dn, requires_master) = keymap[key]
			if re.match("ldap_db_", key) and not cls.master:
				dn = "olcDatabase={2}mdb,cn=config"
			xform = "%s"
			if key == "ldap_common_require_tls":
				xform = "ssf=%s"
			if requires_master and not cls.master:
				Log.logMsg(5, "LDAP: Trying to modify key: %s when not a master" % (key,))
				return (None, None, None)
			else:
				Log.logMsg(5, "Found key %s and dn %s for %s (%s)" % (attr, dn, key, cls.master))
				return (attr, dn, xform)
		else:
			Log.logMsg(1, "UNKNOWN KEY %s" % (key,))

		raise Exception("Key error")

Ldap.initLdap()
