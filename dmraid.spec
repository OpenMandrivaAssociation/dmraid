%define name dmraid
%define version 1.0.0
%define extraver rc16
#define pre pre1
%define rel 1

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

Summary: Device-mapper ATARAID tool
Name: %{name}
Version: %{version}
Release: %{release}
Source0: http://people.redhat.com/~heinzm/sw/dmraid/src/dmraid-%{version}%{extrasrc}.tar.bz2

# From RedHat
Patch1:	ddf1_lsi_persistent_name.patch
Patch2: pdc_raid10_failure.patch
# /From RedHat
Patch3: lib-events-libdmraid-events-isw-strfmt.patch

License: GPL
Group: System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL: http://people.redhat.com/~heinzm
Requires:       kpartx >= 0.4.8-16
Requires:       dmraid-events
BuildRequires:  device-mapper-devel >= 1.02.02
BuildRequires:  device-mapper-event-devel
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

%prep
%setup -q -n %{name}/%{version}.%{extraver}
%patch1 -p1 -b .ddf1_lsi_persistent_name
%patch2 -p1 -b .pdc_raid10_failure
%patch3 -p1 -b .libdmraid_events_isw_strfmt

%build
%if %{use_dietlibc}
CFLAGS="%{optflags} -D_BSD_SOURCE" \
%configure2_5x --enable-dietlibc --disable-libselinux
%else
%configure2_5x --enable-static_link --disable-libselinux
%endif
make
mv tools/dmraid tools/dmraid-static
make clean
%configure --with-user=`id -un` --with-group=`id -gn`
make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_libdir} %{buildroot}/sbin
%makeinstall -s sbindir=%{buildroot}/sbin
install tools/dmraid-static %{buildroot}/sbin
rm -rf %{buildroot}%{_includedir}/dmraid

%clean
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc CHANGELOG KNOWN_BUGS README TODO doc/dmraid_design.txt
%attr(755,root,root) /sbin/dmraid
%attr(755,root,root) /sbin/dmraid-static
%{_mandir}/man8/dmraid.8*
%exclude %{_libdir}


