# Copyright Xervmon inc.
# The official homepage is at http://www.xervmon.com/xervmon_broker


Summary:   Nagios agent and check plugin by Xervmon for efficient remote monitoring
Name:      xervmon_broker
Version:   (automatically inserted)
Release:   1
License:   GPL
Group:     System/Monitoring
URL:       http://xervmon.com/xmd
Source:    xervmon_broker-%{version}.tar.gz
BuildRoot: /tmp/rpm.buildroot.xervmon_broker-%{version}
AutoReq:   off
AutoProv:  off
BuildArch: noarch


%description
xervmon_broker is a xinetd-based remote agent for monitoring Linux and Unix-Servers
with Nagios plus a Check-Plugin xervmon_broker written in Python.
This package is only needed on the Nagios server.

%package agent
Group:     System/Monitoring
Requires:  xinetd, time
Summary: Linux-Agent for xervmon_broker
AutoReq:   off
AutoProv:  off
Conflicts: xervmon_broker-caching-agent xervmon_broker-agent-scriptless
%description agent
This package contains the agent for xervmon_broker. Install this on
all Linux machines you want to monitor via xervmon_broker. You'll need
xinetd to run this agent.

%package agent-scriptless
Group:     System/Monitoring
Requires:  xinetd, time
Summary: Linux-Agent for xervmon_broker
AutoReq:   off
AutoProv:  off
Conflicts: xervmon_broker-caching-agent xervmon_broker-agent
%description agent-scriptless
This package contains the agent for xervmon_broker. Install this on
all Linux machines you want to monitor via xervmon_broker. You'll need
xinetd to run this agent. This package does not run any scripts during
installation. You will need to manage the xinetd configuration on your
own.

%package caching-agent
Group:     System/Monitoring
Requires:  xinetd, time
Summary: Caching Linux-Agent for xervmon_broker
AutoReq:   off
AutoProv:  off
Conflicts: xervmon_broker-agent agent-scriptless
%description caching-agent
This package contains the agent for xervmon_broker with an xinetd
configuration that wrap the agent with the xervmon_broker_caching_agent
wrapper. Use it when doing fully redundant monitoring, where
an agent is regularily polled by more than one monitoring
server.

%package agent-logwatch
Group:     System/Monitoring
Requires:  xervmon_broker-agent, python
Summary: Logwatch-Plugin for xervmon_broker agent
AutoReq:   off
AutoProv:  off
%description agent-logwatch
The logwatch plugin for the xervmon_broker agent allows you to monitor
logfiles on Linux and UNIX. In one or more configuration files you
specify patters for log messages that should raise a warning or
critical state. For each logfile the current position is remembered.
This way only new messages are being sent.

%package agent-oracle
Group:     System/Monitoring
Requires:  xervmon_broker-agent
Summary: ORACLE-Plugin for xervmon_broker agent
AutoReq:   off
AutoProv:  off
%description agent-oracle
The ORACLE plugin for the xervmon_broker agent allows you to monitor
several aspects of ORACLE databases. You need to adapt the
script /etc/xervmon_broker/sqlplus.sh to your needs.

%package web
Group:     System/Monitoring
Requires:  python
Summary: Check_mk web pages
AutoReq:   off
AutoProv:  off
%description web
This package contains the Check_mk webpages. They allow you to
search for services and apply Nagios commands to the search results.

%prep
%setup -q

%install
R=$RPM_BUILD_ROOT
rm -rf $R
DESTDIR=$R ./setup.sh --yes
rm -vf $R/etc/xervmon_broker/*.mk-*

# install agent
mkdir -p $R/etc/xinetd.d
mkdir -p $R/usr/share/doc/xervmon_broker_agent
install -m 644 COPYING ChangeLog AUTHORS $R/usr/share/doc/xervmon_broker_agent
install -m 644 $R/usr/share/xervmon_broker/agents/xinetd.conf $R/etc/xinetd.d/xervmon_broker
install -m 644 $R/usr/share/xervmon_broker/agents/xinetd_caching.conf $R/etc/xinetd.d/xervmon_broker_caching
mkdir -p $R/usr/bin
install -m 755 $R/usr/share/xervmon_broker/agents/xervmon_broker_agent.linux $R/usr/bin/xervmon_broker_agent
install -m 755 $R/usr/share/xervmon_broker/agents/xervmon_broker_caching_agent.linux $R/usr/bin/xervmon_broker_caching_agent
install -m 755 $R/usr/share/xervmon_broker/agents/waitmax $R/usr/bin
install -m 755 $R/usr/share/xervmon_broker/agents/mk-job $R/usr/bin
mkdir -p $R/usr/lib/xervmon_broker_agent/plugins
mkdir -p $R/usr/lib/xervmon_broker_agent/local
mkdir -p $R/var/lib/xervmon_broker_agent
mkdir -p $R/var/lib/xervmon_broker_agent/job

# logwatch and oracle extension
install -m 755 $R/usr/share/xervmon_broker/agents/plugins/mk_logwatch $R/usr/lib/xervmon_broker_agent/plugins
install -m 755 $R/usr/share/xervmon_broker/agents/plugins/mk_oracle $R/usr/lib/xervmon_broker_agent/plugins
install -m 644 $R/usr/share/xervmon_broker/agents/logwatch.cfg $R/etc/xervmon_broker
install -m 755 $R/usr/share/xervmon_broker/agents/sqlplus.sh   $R/etc/xervmon_broker

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%config(noreplace) /etc/xervmon_broker/main.mk
%config(noreplace) /etc/xervmon_broker/multisite.mk
/etc/xervmon_broker/conf.d/README
%config(noreplace) /etc/nagios/objects/*
/usr/bin/xervmon_broker
/usr/bin/cmk
/usr/bin/mkp
%dir /usr/share/xervmon_broker
/usr/share/xervmon_broker/agents
/usr/share/xervmon_broker/checks
/usr/share/xervmon_broker/notifications
/usr/share/xervmon_broker/modules
/usr/share/xervmon_broker/pnp-templates/*
/usr/share/xervmon_broker/xervmon_broker_templates.cfg
/usr/share/doc/xervmon_broker
%dir /var/lib/xervmon_broker
%dir %attr(-,nagios,root) /var/lib/xervmon_broker/counters
%dir %attr(-,nagios,root) /var/lib/xervmon_broker/cache
%dir %attr(-,nagios,root) /var/lib/xervmon_broker/logwatch
%dir /var/lib/xervmon_broker/autochecks
%dir /var/lib/xervmon_broker/precompiled
%dir /var/lib/xervmon_broker/packages
/var/lib/xervmon_broker/packages/xervmon_broker

# Spaeter Subpaket draus machen
/usr/bin/unixcat
/usr/lib/xervmon_broker/livestatus.o
/usr/lib/xervmon_broker/livecheck

%files agent
%config(noreplace) /etc/xinetd.d/xervmon_broker
/usr/bin/xervmon_broker_agent
/usr/bin/waitmax
/usr/bin/mk-job
/usr/share/doc/xervmon_broker_agent
%dir /usr/lib/xervmon_broker_agent/local
%dir /usr/lib/xervmon_broker_agent/plugins
%dir /var/lib/xervmon_broker_agent
%dir %attr(1777,-,-)/var/lib/xervmon_broker_agent/job

%files agent-scriptless
%config(noreplace) /etc/xinetd.d/xervmon_broker
/usr/bin/xervmon_broker_agent
/usr/bin/waitmax
/usr/bin/mk-job
/usr/share/doc/xervmon_broker_agent
%dir /usr/lib/xervmon_broker_agent/local
%dir /usr/lib/xervmon_broker_agent/plugins
%dir /var/lib/xervmon_broker_agent
%dir %attr(1777,-,-)/var/lib/xervmon_broker_agent/job

%files caching-agent
%config(noreplace) /etc/xinetd.d/xervmon_broker_caching
/usr/bin/xervmon_broker_agent
/usr/bin/xervmon_broker_caching_agent
/usr/bin/waitmax
/usr/bin/mk-job
/usr/share/doc/xervmon_broker_agent
%dir /usr/lib/xervmon_broker_agent/local
%dir /usr/lib/xervmon_broker_agent/plugins
%dir /etc/xervmon_broker
%dir /var/lib/xervmon_broker_agent
%dir %attr(1777,-,-)/var/lib/xervmon_broker_agent/job

%files agent-logwatch
/usr/lib/xervmon_broker_agent/plugins/mk_logwatch
%config(noreplace) /etc/xervmon_broker/logwatch.cfg

%files agent-oracle
/usr/lib/xervmon_broker_agent/plugins/mk_oracle
%config(noreplace) /etc/xervmon_broker/sqlplus.sh

%files web
/usr/share/xervmon_broker/web
%config(noreplace) /etc/apache2/conf.d/*

%pre
# Make sure user 'nagios' exists
RUNUSER=nagios
if ! id $RUNUSER > /dev/null 2>&1
then
    useradd -r -c 'Nagios' -d /var/lib/nagios nagios
    echo "Created user nagios"
fi

%define reload_xinetd if [ -x /etc/init.d/xinetd ] ; then if pgrep -x xinetd >/dev/null ; then echo "Reloading xinetd..." ; /etc/init.d/xinetd reload ; else echo "Starting xinetd..." ; /etc/init.d/xinetd start ; fi ; fi

%define activate_xinetd if which chkconfig >/dev/null 2>&1 ; then echo "Activating startscript of xinetd" ; chkconfig xinetd on ; fi

%pre agent
if [ ! -x /etc/init.d/xinetd ] ; then
    echo
    echo "---------------------------------------------"
    echo "WARNING"
    echo
    echo "This package needs xinetd to be installed. "
    echo "Currently you do not have installed xinetd. "
    echo "Please install and start xinetd or install "
    echo "and setup another inetd manually."
    echo ""
    echo "It's also possible to monitor via SSH without "
    echo "an inetd."
    echo "---------------------------------------------"
    echo
fi

%post agent
%activate_xinetd
%reload_xinetd

%postun agent
%reload_xinetd

# Sorry. I need to copy&paste all scripts from the normal agent to 
# the caching agent. This might better be done with RPM macros. But
# that are very ugly if you want to do multi line shell scripts...
%pre caching-agent
if [ ! -x /etc/init.d/xinetd ] ; then
    echo
    echo "---------------------------------------------"
    echo "WARNING"
    echo
    echo "This package needs xinetd to be installed. "
    echo "Currently you do not have installed xinetd. "
    echo "Please install and start xinetd or install "
    echo "and setup another inetd manually."
    echo ""
    echo "It's also possible to monitor via SSH without "
    echo "an inetd."
    echo "---------------------------------------------"
    echo
fi

%post caching-agent
%activate_xinetd
%reload_xinetd

%postun caching-agent
%reload_xinetd

