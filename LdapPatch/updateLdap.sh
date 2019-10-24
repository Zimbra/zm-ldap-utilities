# !/bin/bash 

if [ $USER != "root" ]; then
  echo -e "\n[Error] - User must be root to execute this script..\n"
  exit 0
fi

# set required permissions
chown -R zimbra:zimbra ../LdapPatch
chmod -R o+w /opt/zimbra/common/etc/openldap/schema  
chmod o+w /opt/zimbra/conf/zimbra.ldif
chmod +w /opt/zimbra/conf/attrs/zimbra-attrs.xml
chmod -R o+w /opt/zimbra/common/etc/openldap/zimbra

patchDir=`pwd`
su - zimbra -c "cd $patchDir && ant update-ldap-schema -Dzimbra.buildinfo.version=8.8.15"
su - zimbra -c "cd $patchDir && perl processLdap.pl"

