%define name dmraid
%define version 1.0.0
%define extraver rc16
#define pre pre1
%define rel 1

# from lib/version.h
%define drmajor 1
%define drlibname %mklibname dmraid %drmajor
%define drdevname %mklibname dmraid -d

# we need the libs in /lib(64) as /usr might not be mounted
%define _libdir /%{_lib}

# yes this sucks, but it has to
%if %{?extraver:1}%{?!extraver:0}
%if %{?pre:1}%{?!pre:0}
%define release %manbo_mkrel 0.%{extraver}.0.%{pre}.%{rel}
%define extrasrc .%{extraver}-%{pre}
%else
%define release %manbo_mkrel 0.%{extraver}.%{rel}
%define extrasrc .%{extraver}
%endif
%endif

%ifarch %{ix86} x86_64
%define use_dietlibc 0
%else
%define use_dietlibc 0
%endif

%{?_with_dietlibc: %{expand: %%global use_dietlibc 1}}
%{?_without_dietlibc: %{expand: %%global use_dietlibc 0}}

# Building of dmraid-event-logwatch (disabled by default)
%define build_logwatch 0
%{?_with_logwatch: %{expand: %%global build_logwatch 1}}
%{?_without_logwatch: %{expand: %%global build_logwatch 0}}

Summary: Device-mapper ATARAID tool
Name:	 %{name}
Version: %{version}
Release: %{release}
Source0: http://people.redhat.com/~heinzm/sw/dmraid/src/dmraid-%{version}%{extrasrc}.tar.bz2

# From RedHat
Patch1:	ddf1_lsi_persistent_name.patch
Patch2:	pdc_raid10_failure.patch
Patch4:	avoid_register.patch
Patch6:	libversion.patch
Patch7:	libversion-display.patch
# /From RedHat
Patch3:	lib-events-libdmraid-events-isw-strfmt.patch
Patch5:	fix-linking.patch
Patch8:	libdmraid-events-install.patch

License: GPLv2+
Group:   System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL: http://people.redhat.com/~heinzm
Requires:	kpartx >= 0.4.8-16
Requires:	%{drlibname} = %{version}-%{release}
Requires:	dmraid-events = %{version}-%{release}
BuildRequires:	device-mapper-devel >= 1.02.02
BuildRequires:	device-mapper-event-devel >= 1.02.02
%if %{use_dietlibc}
BuildRequires: dietlibc-devel
%else
BuildRequires: glibc-static-devel
%endif

%description
dmraid (Device-Mapper Raid tool) supports RAID device discovery, RAID
set activation, creation, removal, rebuild and display of properties for
ATARAID/DDF1 metadata.

dmraid uses libdevmapper and the device-mapper kernel runtime to create
devices with respective mappings for the ATARAID sets discovered.

The following ATARAID types are supported:

Adaptec HostRAID ASR
Highpoint HPT37X
Highpoint HPT45X
Intel Software RAID
JMicron JMB36x
LSI Logic MegaRAID
NVidia NForce
Promise FastTrack
Silicon Image Medley
SNIA DDF1
VIA Software RAID


%package -n %{drlibname}
Summary:  Libraries for dmraid
Group:    System/Libraries

%description -n %{drlibname}
Provides libraries for dmraid.


%package -n %{drdevname}
Summary:  Development libraries and headers for dmraid
Group:    Development/Libraries

%description -n %{drdevname}
Provides a library interface for RAID device discovery, RAID set
activation and display of properties for ATARAID volumes.


%package events
Summary:  Dmraid event tool
Group:    System Environment/Base
Requires: dmraid = %{version}-%{release}
Requires: device-mapper-event  >= 1.02.02

%description events
Provides a dmeventd DSO and the dmevent_tool to register devices with it
for device monitoring. All active RAID sets should be manually registered
with dmevent_tool.


%if %{build_logwatch}
%package events-logwatch
Summary:  Dmraid logwatch-based email reporting
Group:    System Environment/Base
Requires: dmraid-events = %{version}-%{release}, logwatch, /etc/cron.d

%description events-logwatch
Provides device failure reporting via logwatch-based email reporting.
Device failure reporting has to be activated manually by activating the
/etc/cron.d/dmeventd-logwatch entry and by calling the dmevent_tool
(see manual page for examples) for any active RAID sets.
%endif


%prep
%setup -q -n %{name}/%{version}.%{extraver}
%patch1 -p1 -b .ddf1_lsi_persistent_name
%patch2 -p1 -b .pdc_raid10_failure
%patch3 -p1 -b .libdmraid_events_isw_strfmt
%patch4 -p1 -b .avoid_register
%patch5 -p1 -b .linking
%patch6 -p1 -b .libversion
%patch7 -p1 -b .libversion_display
%patch8 -p1 -b .lib_events_install


%build
%define common_configure_parameters --with-user=`id -un` --with-group=`id -gn` --disable-libselinux --disable-libsepol --enable-led --enable-intel_led
%if %{use_dietlibc}
CFLAGS="%{optflags} -D_BSD_SOURCE" \
%configure2_5x --enable-dietlibc %{common_configure_parameters}
%else
%configure2_5x --enable-static_link %{common_configure_parameters}
%endif
make
mv tools/dmraid tools/dmraid-static
make clean
%configure2_5x %{common_configure_parameters} --enable-dynamic_link
make


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}{%{_libdir},/sbin,/var/lock/dmraid,/etc/cron.d/,/etc/logwatch/conf/services/,/etc/logwatch/scripts/services/}
%makeinstall -s sbindir=%{buildroot}/sbin
install tools/dmraid-static %{buildroot}/sbin
install -m 644 include/dmraid/*.h %{buildroot}%{_includedir}/dmraid/

%if %{build_logwatch}
# Install logwatch config file and script for dmeventd
install -m 644 logwatch/dmeventd.conf %{buildroot}/etc/logwatch/conf/services/dmeventd.conf
install -m 755 logwatch/dmeventd %{buildroot}/etc/logwatch/scripts/services/dmeventd
install -m 644 logwatch/dmeventd_cronjob.txt %{buildroot}/etc/cron.d/dmeventd-logwatch
install -m 0700 /dev/null %{buildroot}/etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif


%clean
rm -rf %{buildroot}

%post   -n %{drlibname} -p /sbin/ldconfig
%postun -n %{drlibname} -p /sbin/ldconfig


%files
%defattr(644,root,root,755)
%doc CHANGELOG KNOWN_BUGS README TODO doc/dmraid_design.txt
%attr(755,root,root) /sbin/dmraid
%attr(755,root,root) /sbin/dmraid-static
%{_mandir}/man8/dmraid.8*
/var/lock/dmraid

%files -n %{drlibname}
%defattr(644,root,root,755)
%{_libdir}/libdmraid.so.%{drmajor}*

%files -n %{drdevname}
%defattr(-,root,root)
%dir %{_includedir}/dmraid
%{_includedir}/dmraid/*
%{_libdir}/libdmraid.a
%{_libdir}/libdmraid.so

%files events
%defattr(-,root,root)
%attr(755,root,root) /sbin/dmevent_tool
%{_libdir}/libdmraid-events-isw.so*
%{_mandir}/man8/dmevent_tool*

%if %{build_logwatch}
%files events-logwatch
%defattr(-,root,root)
%config(noreplace) /etc/logwatch/*
%config(noreplace) /etc/cron.d/dmeventd-logwatch
%ghost /etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif
