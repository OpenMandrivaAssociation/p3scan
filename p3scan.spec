%define name	p3scan
%define version	3.0
%define release 0.rc1.6

Summary:	Virus scanning transparent proxy server for POP3
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPLv2+
Group:		Networking/Mail
URL:		http://p3scan.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}_rc1.tar.gz
Patch0:		%{name}-iptables-rules.patch
BuildRequires:	pcre-devel
BuildRequires:	openssl-devel
BuildRequires:	clamav-devel
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
%setup -q -n %{name}-%{version}_rc1
%patch0 -p0

%build
%serverbuild
%configure --with-user=clamav
%make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/var/spool/%{name}/children
mkdir -p %{buildroot}/var/spool/%{name}/notify
mkdir -p %{buildroot}/var/run/%{name}

%makeinstall_std

mkdir -p %{buildroot}/%{_sysconfdir}/%{name}
cat << EOF >%{buildroot}%{_sysconfdir}/%{name}/redirect_on.sh
#!/bin/bash
iptables -t nat -A PREROUTING -p tcp -i lo --dport pop3 -j REDIRECT --to 8110
iptables -t nat -I OUTPUT -p tcp --dport 110 -j REDIRECT --to 8110
iptables -t nat -I OUTPUT -p tcp --dport 110 -m owner --uid-owner clamav -j ACCEPT
/etc/init.d/iptables restart
EOF
cat << EOF >%{buildroot}%{_sysconfdir}/%{name}/redirect_off.sh
#!/bin/bash
iptables -t nat -D PREROUTING -p tcp -i lo --dport pop3 -j REDIRECT --to 8110
iptables -t nat -D OUTPUT -p tcp --dport 110 -j REDIRECT --to 8110
iptables -t nat -D OUTPUT -p tcp --dport 110 -m owner --uid-owner clamav -j ACCEPT
/etc/init.d/iptables restart
EOF

chmod 755 %{buildroot}%{_sysconfdir}/%{name}/redirect*

#dirty workaround, --docdir seems not to work (to fix)
mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}/usr/doc/%{name}-%{version}_rc1 %{buildroot}%{_docdir}/%{name}

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
%doc AUTHORS CONTRIBUTERS NEWS README README-rpm spamfaq.html
%{_bindir}/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*
%{_sysconfdir}/init.d/%{name}
%{_mandir}/man8/*
%defattr(-,clamav,mail)
%dir /var/spool/%{name}
%dir /var/spool/%{name}/*
/var/run/%{name}


