#!/usr/bin/perl
#
# ***** BEGIN LICENSE BLOCK *****
# Zimbra Collaboration Suite Server
# Copyright (C) 2015, 2016 Synacor, Inc.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****
#
use strict;
use lib '/opt/zimbra/common/lib/perl5';
use Net::LDAP;
use XML::Simple;

if ( !-d "/opt/zimbra/common/etc/openldap/schema" ) {
    warn "ERROR: openldap does not appear to be installed - exiting\n";
    exit(1);
}

my $id = getpwuid($<);
chomp $id;
if ( $id ne "zimbra" ) {
    warn "Error: must be run as zimbra user\n";
    exit(1);
}

my $localxml           = XMLin("/opt/zimbra/conf/localconfig.xml");
my $ldap_root_password = $localxml->{key}->{ldap_root_password}->{value};
my $ldap_is_master     = $localxml->{key}->{ldap_is_master}->{value};
chomp($ldap_is_master, $ldap_root_password);

if ( lc($ldap_is_master) ne "true" ) {
    exit 0;
}

my $ldap =
  Net::LDAP->new('ldapi://%2fopt%2fzimbra%2fdata%2fldap%2fstate%2frun%2fldapi/')
  or die "$@";

my $mesg = $ldap->bind( "cn=config", password => "$ldap_root_password" );

$mesg->code && die "Bind: " . $mesg->error . "\n";

$mesg = $ldap->search(
    base   => "cn=accesslog",
    filter => "(objectClass=*)",
    scope  => "base",
    attrs  => ['1.1'],
);
if ( $mesg->count > 0 ) {
    my $bdn = "olcDatabase={3}mdb,cn=config";

    $mesg = $ldap->search(
        base   => "$bdn",
        filter => "(olcOverlay=syncprov)",
        scope  => "sub",
        attrs  => ['1.1'],
    );

    if ( $mesg->count == 0 ) {
        warn 
"ERROR: This is a master, with an accesslog, and syncprov is missing.\n";
        $ldap->unbind;
        exit 1;
    }
    else {
        my $dn = $mesg->entry(0)->dn;

        $mesg = $ldap->search(
            base   => "$bdn",
            filter => "(olcSpSessionLog=*)",
            scope  => "sub",
            attrs  => ['olcSpSessionLog'],
        );

        if ( $mesg->count == 0 ) {
            $mesg =
              $ldap->modify( "$dn", add => { olcSpSessionlog => '10000000' }, );
            $mesg->code && warn "failed to add entry: ", $mesg->error;
            $ldap->unbind;
            exit 0;
        }
    }
}
else {
    $ldap->unbind;
    exit 0;
}
