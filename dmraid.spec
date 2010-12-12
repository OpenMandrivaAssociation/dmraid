%define name dmraid
%define version 1.0.0
%define extraver rc16
#define pre pre1
%define rel 3

# from lib/version.h
%define drmajor 1
%define drlibname %mklibname dmraid %drmajor
%define drdevname %mklibname dmraid -d

# we need the libs in /lib(64) as /usr might not be mounted
%define _libdir /%{_lib}
%define _usrlibdir /usr/%{_lib}

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

# (bluca) since fedora/redhat rpm is the real upstream for dmraid
# patch numbers < 100 are reserved for patches synced from fedora/redhat
# patch numbers > 100 are for our distro specific patches
Patch0: dmraid-1.0.0.rc16-test_devices.patch
Patch1:	ddf1_lsi_persistent_name.patch
Patch2:	pdc_raid10_failure.patch
Patch3:	return_error_wo_disks.patch
Patch4: fix_sil_jbod.patch
Patch5:	avoid_register.patch
#we dont use this# Patch6: move_pattern_file_to_var.patch
Patch7:	libversion.patch
Patch8:	libversion-display.patch
Patch9: bz635995-data_corruption_during_activation_volume_marked_for_rebuild.patch
# Patch10: bz626417_8-faulty_message_after_unsuccessful_vol_registration.patch
Patch11: bz626417_19-enabling_registration_degraded_volume.patch
Patch12: bz626417_20-cleanup_some_compilation_warning.patch
Patch13: bz626417_21-add_option_that_postpones_any_metadata_updates.patch

Patch101:	lib-events-libdmraid-events-isw-strfmt.patch
Patch102:	fix-linking.patch
Patch103:	libdmraid-events-soname.patch
Patch104:	libdmraid-events-install.patch

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
Group:    System/Libraries

%description -n %{drdevname}
Provides a library interface for RAID device discovery, RAID set
activation and display of properties for ATARAID volumes.


%package events
Summary:  Dmraid event tool
Group:    System/Base
Requires: dmraid = %{version}-%{release}
Requires: device-mapper-event  >= 1.02.02

%description events
Provides a dmeventd DSO and the dmevent_tool to register devices with it
for device monitoring. All active RAID sets should be manually registered
with dmevent_tool.


%if %{build_logwatch}
%package events-logwatch
Summary:  Dmraid logwatch-based email reporting
Group:    System/Base
Requires: dmraid-events = %{version}-%{release}, logwatch, /etc/cron.d

%description events-logwatch
Provides device failure reporting via logwatch-based email reporting.
Device failure reporting has to be activated manually by activating the
/etc/cron.d/dmeventd-logwatch entry and by calling the dmevent_tool
(see manual page for examples) for any active RAID sets.
%endif


%prep
%setup -q -n %{name}/%{version}.%{extraver}
%patch0 -p1 -b .test_devices
%patch1 -p1 -b .ddf1_lsi_persistent_name
%patch2 -p1 -b .pdc_raid10_failure
%patch3 -p1 -b .return_error_wo_disks
%patch4 -p1 -b .fix_sil_jbod
%patch5 -p1 -b .avoid_register
%patch7 -p1 -b .libversion
%patch8 -p1 -b .libversion_display
%patch9 -p1 -b .bz635995
%patch11 -p1 -b .bz626417_19
%patch12 -p1 -b .bz626417_20
%patch13 -p1 -b .bz626417_21

%patch101 -p1 -b .libdmraid_events_isw_strfmt
%patch102 -p1 -b .linking
%patch103 -p1 -b .lib_events_soname
%patch104 -p1 -b .lib_events_install

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
%makeinstall -s sbindir=%{buildroot}/sbin
install tools/dmraid-static %{buildroot}/sbin

mkdir -p %{buildroot}%{_usrlibdir}
mv %{buildroot}%{_libdir}/libdmraid.a %{buildroot}%{_usrlibdir}
# cannot move .so symlink to %{_usrlibdir}, there is some build
# macro that recreates it every time
#ln -s %{_libdir}/libdmraid.so.%{drmajor} %{buildroot}%{_usrlibdir}/libdmraid.so
#rm -f %{_libdir}/libdmraid.so

mkdir -p %{buildroot}/var/lock/dmraid

%if %{build_logwatch}
# Install logwatch config file and script for dmeventd
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}/etc/logwatch/conf/services
mkdir -p %{buildroot}/etc/logwatch/scripts/services
install -m 644 logwatch/dmeventd.conf %{buildroot}/etc/logwatch/conf/services/dmeventd.conf
install -m 755 logwatch/dmeventd %{buildroot}/etc/logwatch/scripts/services/dmeventd
install -m 644 logwatch/dmeventd_cronjob.txt %{buildroot}/etc/cron.d/dmeventd-logwatch
install -m 0700 /dev/null %{buildroot}/etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post   -n %{drlibname} -p /sbin/ldconfig
%postun -n %{drlibname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root,755)
%doc CHANGELOG CREDITS KNOWN_BUGS README TODO doc/dmraid_design.txt
/sbin/dmraid
/sbin/dmraid-static
%{_mandir}/man8/dmraid.8*
%dir /var/lock/dmraid

%files -n %{drlibname}
%defattr(-,root,root,755)
%{_libdir}/libdmraid.so.%{drmajor}*

%files -n %{drdevname}
%defattr(644,root,root,755)
%dir %{_includedir}/dmraid
%{_includedir}/dmraid/*.h
%{_usrlibdir}/libdmraid.a
%{_libdir}/libdmraid.so

%files events
%defattr(-,root,root,755)
/sbin/dmevent_tool
%{_libdir}/libdmraid-events-isw.so
%{_mandir}/man8/dmevent_tool*

%if %{build_logwatch}
%files events-logwatch
%defattr(-,root,root,755)
%config(noreplace) /etc/logwatch/*
%config(noreplace) /etc/cron.d/dmeventd-logwatch
%ghost /etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif
