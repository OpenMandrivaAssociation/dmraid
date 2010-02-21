%define name dmraid
%define version 1.0.0
%define extraver rc16
#define pre pre1
### NOTE! THIS IS WIP! DONT SUBMIT IT TO THE BS! /tmb
#define rel 1

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

# we need the libs in /lib(64) as /usr might be unmounted
%define _libdir /%{_lib}

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
Patch3: lib-events-libdmraid-events-isw-strfmt.patch
Patch5:	fix-linking.patch

License: GPLv2+
Group: System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL: http://people.redhat.com/~heinzm
Requires:	kpartx >= 0.4.8-16
Requires:	dmraid-events
BuildRequires:	device-mapper-devel >= 1.02.02
BuildRequires:	device-mapper-event-devel
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

%package devel
Summary: Development libraries and headers for dmraid
Group: Development/Libraries
Requires: dmraid = %{version}-%{release}

%description devel
dmraid-devel provides a library interface for RAID device discovery,
RAID set activation and display of properties for ATARAID volumes.

%package events
Summary: Dmraid event tool
Group: System Environment/Base
Requires: dmraid = %{version}-%{release}
Requires: device-mapper-event

%description events
Provides a dmeventd DSO and the dmevent_tool to register devices with it
for device monitoring. All active RAID sets should be manually registered
with dmevent_tool.

%if %{build_logwatch}
%package events-logwatch
Summary: Dmraid logwatch-based email reporting
Group: System Environment/Base
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
%configure2_5x %{common_configure_parameters}
make


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}{%{_libdir},/sbin,/var/lock/dmraid,/etc/cron.d/,/etc/logwatch/conf/services/,/etc/logwatch/scripts/services/}
%makeinstall -s sbindir=%{buildroot}/sbin
install tools/dmraid-static %{buildroot}/sbin
install -m 644 include/dmraid/*.h %{buildroot}%{_includedir}/dmraid/
rm -rf %{buildroot}%{_libdir}/libdmraid.a

# If requested, install the libdmraid and libdmraid-events (for dmeventd) DSO
install -m 755 lib/libdmraid.so \
	%{buildroot}%{_libdir}/libdmraid.so.%{version}
install -m 755 lib/libdmraid-events-isw.so \
	%{buildroot}%{_libdir}/libdmraid-events-isw.so.%{version}


%if %{build_logwatch}
# Install logwatch config file and script for dmeventd
install -m 644 logwatch/dmeventd.conf %{buildroot}/etc/logwatch/conf/services/dmeventd.conf
install -m 755 logwatch/dmeventd %{buildroot}/etc/logwatch/scripts/services/dmeventd
install -m 644 logwatch/dmeventd_cronjob.txt %{buildroot}/etc/cron.d/dmeventd-logwatch
install -m 0700 /dev/null %{buildroot}/etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%post events -p /sbin/ldconfig
%postun events -p /sbin/ldconfig


%files
%defattr(644,root,root,755)
%doc CHANGELOG KNOWN_BUGS README TODO doc/dmraid_design.txt
%attr(755,root,root) /sbin/dmraid
%attr(755,root,root) /sbin/dmraid-static
%{_mandir}/man8/dmraid.8*
%{_libdir}/libdmraid.so*
/var/lock/dmraid


%files devel
%defattr(-,root,root)
%dir %{_includedir}/dmraid
%{_includedir}/dmraid/*


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
