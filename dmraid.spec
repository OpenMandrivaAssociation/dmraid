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

# From RedHat
Patch1: dmraid-1.0.0.rc15-whitespace.patch
# Fix mismatch between BIOS and dmraid's view of ISW raid 10 sets
Patch2: dmraid-1.0.0.rc15-isw-raid10.patch
# Add --rm_partitions telling the kernel to forget about partitions
# on underlying disk, to event direct access
Patch3: dmraid-1.0.0.rc15-rm_partitions.patch
# Fix activation of isw raid sets when the disks have serialnumber longer
# than 16 characters
Patch4: dmraid-1.0.0.rc15-isw-serial.patch
# /From RedHat

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
%patch1 -p1 -b .whitespace
%patch2 -p1 -b .isw-raid10
%patch3 -p1 -b .rm_partitions
%patch4 -p1 -b .isw-serial

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


