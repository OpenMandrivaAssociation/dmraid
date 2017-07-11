# from lib/version.h
%define	prerel	rc16
%define	major	1
%define	libname	%mklibname dmraid %{major}
%define	devname	%mklibname dmraid -d

# Building of dmraid-event-logwatch (disabled by default)
%bcond_with	logwatch

Summary:	Device-mapper ATARAID tool
Name:		dmraid
Version:	1.0.0
Release:	0.%{prerel}.14
License:	GPLv2+
Group:		System/Kernel and hardware
Url:		http://people.redhat.com/~heinzm
Source0:	http://people.redhat.com/~heinzm/sw/dmraid/src/%{name}-%{version}.%{prerel}.tar.bz2
# (bluca) since fedora/redhat rpm is the real upstream for dmraid
# patch numbers < 100 are reserved for patches synced from fedora/redhat
# patch numbers > 100 are for our distro specific patches
Patch0:		dmraid-1.0.0.rc16-test_devices.patch
Patch1:		ddf1_lsi_persistent_name.patch
Patch2:		pdc_raid10_failure.patch
Patch3:		return_error_wo_disks.patch
Patch4:		fix_sil_jbod.patch
Patch5:		avoid_register.patch
#we dont use this# Patch6: move_pattern_file_to_var.patch
Patch7:		libversion.patch
Patch8:		libversion-display.patch
Patch9:		bz635995-data_corruption_during_activation_volume_marked_for_rebuild.patch
# Patch10: bz626417_8-faulty_message_after_unsuccessful_vol_registration.patch
Patch11:	bz626417_19-enabling_registration_degraded_volume.patch
Patch12:	bz626417_20-cleanup_some_compilation_warning.patch
Patch13:	bz626417_21-add_option_that_postpones_any_metadata_updates.patch

Patch101:	lib-events-libdmraid-events-isw-strfmt.patch
Patch102:	fix-linking.patch
Patch103:	libdmraid-events-soname.patch
Patch104:	libdmraid-events-install.patch
Patch105:	dmraid-1.0.0.rc16-library-linking-fix.patch
Patch106:	dmraid-1.0.0.rc16-log-notice.patch
Patch107:	dmraid-1.0.0.rc16-add-missing-libdl-linkage.patch
Patch108:	respect-ldflags.patch

BuildRequires:	pkgconfig(devmapper)
BuildRequires:	pkgconfig(devmapper-event)
BuildRequires:	pkgconfig(lvm2app)
Requires:	kpartx >= 0.4.8-16
Requires:	dmraid-events = %{version}-%{release}
Requires:	dmsetup

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

%package -n	%{libname}
Summary:	Libraries for dmraid
Group:		System/Libraries

%description -n	%{libname}
Provides libraries for dmraid.

%package -n	%{devname}
Summary:	Development libraries and headers for dmraid
Group:		System/Libraries
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
Provides a library interface for RAID device discovery, RAID set
activation and display of properties for ATARAID volumes.

%package	events
Summary:	Dmraid event tool
Group:		System/Base
Requires:	dmraid = %{version}-%{release}
Requires:	device-mapper-event >= 1.02.02

%description	events
Provides a dmeventd DSO and the dmevent_tool to register devices with it
for device monitoring. All active RAID sets should be manually registered
with dmevent_tool.

%if %{with logwatch}
%package	events-logwatch
Summary:	Dmraid logwatch-based email reporting
Group:		System/Base
Requires:	dmraid-events = %{version}-%{release} logwatch

%description	events-logwatch
Provides device failure reporting via logwatch-based email reporting.
Device failure reporting has to be activated manually by activating the
/etc/cron.d/dmeventd-logwatch entry and by calling the dmevent_tool
(see manual page for examples) for any active RAID sets.
%endif

%prep
%setup -qn %{name}/%{version}.%{prerel}
%apply_patches
autoreconf -fiv

%build
export CC=gcc

%configure \
	--libdir=/%{_lib} \
	--sbindir=/sbin \
	--with-user=`id -un` \
	--with-group=`id -gn` \
	--disable-libselinux \
	--disable-libsepol \
	--enable-led \
	--enable-intel_led \
	--enable-shared_lib
%make -j1

%install
%makeinstall  -s sbindir=%{buildroot}/sbin libdir=%{buildroot}/%{_lib}
chmod u+w -R %{buildroot}
chmod 644 %{buildroot}%{_includedir}/dmraid/*.h

mkdir -p %{buildroot}%{_libdir}
rm %{buildroot}/%{_lib}/libdmraid.{a,so}
ln -sr %{buildroot}/%{_lib}/libdmraid.so.%{major} %{buildroot}%{_libdir}/libdmraid.so

mkdir -p %{buildroot}/var/lock/dmraid

%if %{with logwatch}
# Install logwatch config file and script for dmeventd
install -m644 logwatch/dmeventd.conf -D %{buildroot}/etc/logwatch/conf/services/dmeventd.conf
install -m755 logwatch/dmeventd -D %{buildroot}/etc/logwatch/scripts/services/dmeventd
install -m644 logwatch/dmeventd_cronjob.txt -D %{buildroot}/etc/cron.d/dmeventd-logwatch
install -m700 /dev/null -D %{buildroot}/etc/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif

%files
%doc CHANGELOG CREDITS KNOWN_BUGS README TODO doc/dmraid_design.txt
/sbin/dmraid
%{_mandir}/man8/dmraid.8*
%dir /var/lock/dmraid

%files -n %{libname}
/%{_lib}/libdmraid.so.%{major}*

%files -n %{devname}
%dir %{_includedir}/dmraid
%{_includedir}/dmraid/*.h
%{_libdir}/libdmraid.so

%files events
/sbin/dmevent_tool
/%{_lib}/libdmraid-events-isw.so
%{_mandir}/man8/dmevent_tool*

%if %{with logwatch}
%files events-logwatch
%config(noreplace) %{_sysconfdir}/logwatch/*
%config(noreplace) %{_sysconfdir}/cron.d/dmeventd-logwatch
%ghost %{_sysconfdir}/logwatch/scripts/services/dmeventd_syslogpattern.txt
%endif
