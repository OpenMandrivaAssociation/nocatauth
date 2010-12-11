%define realname NoCatAuth
%define sname nocat
Summary:	Third party wireless authentication system
Name:		nocatauth
Version:	0.82
Release: 	%mkrel 11
License:        GPL
Group:		Networking/Remote access
Source0:	http://nocat.net/download/NoCatAuth/NoCatAuth-0.82.tar.bz2
Source1:	pgp-response.txt
Source2:        NoCatAuthSetup.txt
Patch0:		%{name}-mdk-build.patch
URL:            http://nocat.net
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:	iptables gnupg
BuildArchitectures:	noarch
Requires:	webserver mod_ssl gnupg

%description
The NoCatAuth project implements a third party wireless authentication 
system (or Auth system, for short). Written in Perl and C, it takes care 
of presenting the user with a login prompt, contacts a MySQL database to 
lookup user credentials, securely notifies the wireless gateway of the 
user's status, and authorizes further access. 

Note: The packaged gnupg keys are just using fairly generic values. You 
will most likely want to generate your own and put them on your authserve
and gateway.

Note2: You will need to configure /etc/httpd/conf.d/74_authserv.conf for 
your network.  A sample vhost stanza is provided.

%package gateway
Summary:	NoCatauth gateway
Group:		Networking/Remote access
Requires:	iptables iproute2 chkconfig gnupg
BuildArchitectures:	noarch
Requires(post,preun):		rpm-helper

%description gateway
The NoCatAuth gateway manages local connections, sets bandwidth throttling 
and firewall rules, and times out old logins after a user specified time 
limit. While the gateway and auth system can be run on the same machine, 
it is strongly recommended that the auth system reside on a separate, more 
tightly secured machine than the gateway.  If you do want to run both on 
the same machine or subnet, you'll need the Net::Netmask perl module.

Note: The packaged gnupg keys are just using fairly generic values. You 
will most likely want to generate your own and put them on your authserve
and gateway.

Note2: You will need to configure /etc/nocat/gateway.conf for your 
network. Specifically, you'll need to define AuthServiceAddr.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -q -n %{realname}-%{version}
%patch0 -p1 -b .mdk
cp %SOURCE1 .
cp %SOURCE2 .

%build
perl -pi -e 's|Linux 2.4|Linux 2.6|g' bin/detect-fw.sh
make PREFIX=%{_datadir}/nocat/authserv authserv DESTDIR=$RPM_BUILD_ROOT
make PREFIX=%{_datadir}/nocat/authserv pgpkey DESTDIR=$RPM_BUILD_ROOT
make PREFIX=%{_datadir}/nocat/gw gateway DESTDIR=$RPM_BUILD_ROOT

%install
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install etc/nocat.rc $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/init.d/%{name}-gateway
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{sname}
mv $RPM_BUILD_ROOT%{_datadir}/%{sname}/gw/%{sname}.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{sname}/gateway.conf
mv $RPM_BUILD_ROOT%{_datadir}/%{sname}/authserv/%{sname}.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{sname}/authserv.conf
install etc/exception $RPM_BUILD_ROOT%{_datadir}/%{sname}/gw/bin
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install etc/authserv.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/74_authserv.conf
install -d $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install etc/pam.conf $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/nocat
install -d $RPM_BUILD_ROOT%{_sbindir}
cat > $RPM_BUILD_ROOT/%{_sbindir}/admintool << EOF
#!/bin/sh
export NOCAT=%{_sysconfdir}/nocat/authserv.conf
exec %{_datadir}/%{sname}/authserv/bin/admintool \$*
EOF
chmod 0744 $RPM_BUILD_ROOT/%{_sbindir}/admintool
cp $RPM_BUILD_ROOT%{_datadir}/%{sname}/authserv/trustedkeys.gpg $RPM_BUILD_ROOT%{_datadir}/%{sname}/gw/pgp
chmod 0700 $RPM_BUILD_ROOT%{_datadir}/%{sname}/gw/pgp
 
%post gateway
%_post_service %{name}-gateway

%preun gateway
%_preun_service %{name}-gateway

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc BUGS LICENSE README TODO doc/* etc/nocat.schema NoCatAuthSetup.txt
%dir %{_datadir}/%{sname}
%dir %{_datadir}/%{sname}/authserv
%{_datadir}/%{sname}/authserv/[b-l]*
%{_datadir}/%{sname}/authserv/trustedkeys.gpg
%config(noreplace) %{_sysconfdir}/%{sname}/authserv.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/74_authserv.conf
%config(noreplace) %{_sysconfdir}/pam.d/nocat
%defattr(-,apache,apache)
%{_datadir}/%{sname}/authserv/pgp*
%{_sbindir}/admintool

%files gateway
%defattr(-,root,root)
%doc INSTALL
%dir %{_datadir}/%{sname}/gw
%{_datadir}/%{sname}/gw/*
%config(noreplace) %{_sysconfdir}/%{sname}/gateway.conf
%config(noreplace) %{_sysconfdir}/rc.d/init.d/%{name}-gateway


