%define name dmraid
%define version 1.0.0
%define extraver rc14
#define pre pre1
%define rel 7

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
%define use_dietlibc 1
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
Patch0: dmraid-mdk.patch
Patch1: dmraid-isw_raid10.patch
Patch2: dmraid-isw_raid10_1.patch
Patch4: dmraid-pdc_max_sectors.patch
Patch5: dmraid-pdc_configoffsets.patch
# to be compatible with mkinitrd/nashDmCreatePartitions()
Patch6: dmraid-use-p-separator-in-partition-device-name.patch
# (from RH)
Patch10: dmraid-1.0.0.rc14-jmicron-name.patch
Patch11: dmraid-1.0.0.rc14-solitary-meta-block.patch
Patch12: dmraid-1.0.0.rc14-UUID.patch
Patch13: dmraid-1.0.0.rc14-ERROR.patch
Patch14: dmraid-1.0.0.rc14-UUID-Subsystemprefix.patch

License: GPL
Group: System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL: http://people.redhat.com/~heinzm
BuildRequires:	device-mapper-devel >= 1.00.09
%if %{use_dietlibc}
BuildRequires: dietlibc-devel
%else
BuildRequires: glibc-static-devel
%endif

%description
dmraid (Device-Mapper Raid tool) discovers, [de]activates and displays
properties of software RAID sets (i.e. ATARAID) and contained DOS
partitions using the device-mapper runtime of the 2.6 kernel.

The following ATARAID types are supported on Linux 2.6:

Adaptec HostRAID ASR
Highpoint HPT37X
Highpoint HPT45X
Intel Software RAID
JMicron JMB36X
LSI Logic MegaRAID
NVidia NForce
Promise FastTrack
Silicon Image Medley
VIA Software RAID

%prep
%setup -q -n %{name}/%{version}.%{extraver}
%patch0 -p2 -b .mdk
%patch1 -p1 -b .isw_raid10
%patch2 -p0 -b .isw_raid101
%patch4 -p1 -b .pdc_max_sectors
%patch5 -p0 -b .pdc_configoffsets
%patch6 -p2 -b .p
%patch10 -p1 -b .jmicron-name
%patch11 -p1 -b .solitary-meta-block
%patch12 -p1 -b .UUID
%patch13 -p1 -b .ERROR
%patch14 -p1 -b .UUID-Subsystemprefix

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


