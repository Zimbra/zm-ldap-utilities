#!/usr/bin/perl

use strict;

use Cwd;
use Time::localtime qw(ctime);

our $platform = qx(/opt/zimbra/libexec/get_plat_tag.sh);
chomp $platform;

my $logFileName = "zmsetup.".getDateStamp().".log";
my $logfile = "/tmp/".$logFileName;
open LOGFILE, ">$logfile" or die "Can't open $logfile: $!\n";
unlink("/tmp/zmsetup.log") if (-e "/tmp/zmsetup.log");
symlink($logfile, "/tmp/zmsetup.log");

my $ol = select (LOGFILE);
select ($ol);
$| = 1;

progress("Operations logged to $logfile\n");

our $ZMPROV = "/opt/zimbra/bin/zmprov -r -m -l";
our $SU = "su - zimbra -c ";

my $pwuid = getpwuid( $< );
if ($pwuid eq "zimbra") {
  $SU = "";
}

our %options = ();

if (isInstalled("zimbra-ldap")) {
  installLdapSchema();
}

sub installLdapSchema {
  main::runAsZimbra("/opt/zimbra/libexec/zmldapschema 2>/dev/null");
}

my $rc = runAsZimbra ("/opt/zimbra/libexec/zmldapupdateldif");

sub isInstalled {
  my $pkg = shift;

  my $pkgQuery;

  my $good = 0;
  if ($platform =~ /^DEBIAN/ || $platform =~ /^UBUNTU/) {
    $pkgQuery = "dpkg -s $pkg";
  } else {
    $pkgQuery = "rpm -q $pkg";
  }

  my $rc = 0xffff & system ("$pkgQuery > /dev/null 2>&1");
  $rc >>= 8;
  if (($platform =~ /^DEBIAN/ || $platform =~ /^UBUNTU/) && $rc == 0 ) {
    $good = 1;
    $pkgQuery = "dpkg -s $pkg | egrep '^Status: ' | grep 'not-installed'";
    $rc = 0xffff & system ("$pkgQuery > /dev/null 2>&1");
    $rc >>= 8;
  }
  return ($rc == $good);
}

sub runAsZimbra {
  my $cmd = shift;
  if ($cmd =~ /ldappass/ || $cmd =~ /init/ || $cmd =~ /zmprov -r -m -l ca/) {
    # Suppress passwords in log file
    my $c = (split ' ', $cmd)[0];
    detail ( "*** Running as zimbra user: $c\n" );
  } else {
    detail ( "*** Running as zimbra user: $cmd\n" );
  }
  my $rc;
  $rc = 0xffff & system("$SU \"$cmd\" >> $logfile 2>&1");
  return $rc;
}

sub detail {
  my $msg = shift;
  my ($sub,$line) = (caller(1))[3,2];
  my $date = ctime();
  $msg =~ s/\n$//;
  $msg = "$sub:$line $msg" if $options{d};
  open(LOG, ">>$logfile");
  print LOG "$date $msg\n";
  close(LOG);
}

sub progress {
  my $msg = shift;
  print "$msg";
  my ($sub,$line) = (caller(1))[3,2];
  $msg = "$sub:$line $msg" if $options{d};
  detail ($msg);
}

sub getDateStamp() {
  my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time());
  $year = 1900+$year;
  $sec = sprintf("%02d", $sec);
  $min = sprintf("%02d", $min);
  $hour = sprintf("%02d", $hour);
  $mday = sprintf("%02d", $mday);
  $mon = sprintf("%02d", $mon+1);
  my $stamp = "$year$mon$mday-$hour$min$sec";
  return $stamp;
}
