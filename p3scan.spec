%define name	p3scan
%define version	2.3.2
%define release %mkrel 20

Summary:	Virus scanning transparent proxy server for POP3
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Networking/Mail
URL:		http://p3scan.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2
Source1:    	%{name}.init.bz2
Patch0:		%{name}-2.3.2-mdkconf.patch
Patch1:		%{name}-conf.patch
BuildRequires:	pcre-devel
BuildRequires:	openssl-devel
Requires:	shorewall
Requires:	pcre
Requires:	perl-Mail-SpamAssassin
Requires:	spamassassin-spamc
Requires:	spamassassin-spamd
Requires:	clamd
Requires:	sendmail-command
Requires(pre):	rpm-helper
Conflicts:	pop3vscan
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
This is a full-transparent proxy-server for POP3-Clients. It runs on
a Linux box with iptables (for port re-direction). It can be used to
provide POP3 email scanning from the internet, to any internal network
and is ideal for helping to protect your "Other OS" LAN from harm,
especially when used in conjunction with a firewall and other Internet
Proxy servers.

%prep
%setup -q
%patch0 -p1 -b .mdkconf
%patch1

%build
%serverbuild
%make OPTS="$RPM_OPT_FLAGS" 

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/var/spool/%{name}/children
mkdir -p %{buildroot}/var/spool/%{name}/notify
mkdir -p %{buildroot}/var/run/%{name}

install -m755 %{name} -D %{buildroot}%{_sbindir}/%{name}
install -m644 %{name}.conf -D %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -m644 %{name}-*.mail -D %{buildroot}%{_sysconfdir}/%{name}/
install -m644 %{name}.8.gz -D %{buildroot}%{_mandir}/man8/%{name}.8.gz
install -m644 %{name}_readme.8.gz -D %{buildroot}%{_mandir}/man8/%{name}_readme.8.gz

mkdir -p %{buildroot}/%{_initrddir}/
bzcat %{SOURCE1} >  %{buildroot}/%{_initrddir}/%{name}
chmod 755 %{buildroot}/%{_initrddir}/%{name}

cat << EOF >%{buildroot}%{_sysconfdir}/%{name}/firewall.sh
#!/bin/bash
iptables -t nat -A PREROUTING -p tcp -i lo --dport pop3 -j REDIRECT --to 8110
iptables -t nat -I OUTPUT -p tcp --dport 110 -j REDIRECT --to 8110
iptables -t nat -I OUTPUT -p tcp --dport 110 -m owner --uid-owner clamav -j ACCEPT
/etc/init.d/iptables restart
EOF

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
rm -rf /var/spool/%{name}
rm -rf /var/run/%{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS CHANGELOG CONTRIBUTERS NEWS README README-rpm spamfaq.html TODO.list
%{_sbindir}/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*
%{_initrddir}/%{name}
%{_mandir}/man8/*
%defattr(-,clamav,mail)
%dir /var/spool/%{name}
%dir /var/spool/%{name}/*
/var/run/%{name}


