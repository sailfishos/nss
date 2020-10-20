%global nspr_version 4.29
%global unsupported_tools_directory %{_libdir}/nss/unsupported-tools
%global saved_files_dir %{_libdir}/nss/saved
%global dracutlibdir %{_prefix}/lib/dracut
%global dracut_modules_dir %{dracutlibdir}/modules.d/05nss-softokn/
%global dracut_conf_dir %{dracutlibdir}/dracut.conf.d

%bcond_without tests

# Produce .chk files for the final stripped binaries
#
# NOTE: The LD_LIBRARY_PATH line guarantees shlibsign links	
# against the freebl that we just built. This is necessary
# because the signing algorithm changed on 3.14 to DSA2 with SHA256
# whereas we previously signed with DSA and SHA1. We must Keep this line
# until all mock platforms have been updated.
# After %%{__os_install_post} we would add
# export LD_LIBRARY_PATH=$RPM_BUILD_ROOT/%%{_libdir}
	
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    export LD_LIBRARY_PATH=$RPM_BUILD_ROOT/%{_libdir} \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libsoftokn3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libfreeblpriv3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libfreebl3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libnssdbm3.so \
%{nil}

Summary:          Network Security Services
Name:             nss
Version:          3.58
Release:          1
License:          MPLv2.0
URL:              http://www.mozilla.org/projects/security/pki/nss/
Requires:         nspr >= %{nspr_version}
Requires:         nss-util >= %{version}
Requires:         nss-softokn%{_isa} >= %{version}
Requires:         nss-system-init
Requires:         p11-kit-trust
BuildRequires:    nspr-devel >= %{nspr_version}
BuildRequires:    pkgconfig(sqlite3)
BuildRequires:    zlib-devel
BuildRequires:    pkgconfig
BuildRequires:    gawk
BuildRequires:    psmisc
BuildRequires:    perl

Source0:          %{name}-%{version}.tar.gz
Source1:          nss-util.pc.in
Source2:          nss-util-config.in
Source3:          nss-softokn.pc.in
Source4:          nss-softokn-config.in
Source6:          nss-softokn-dracut-module-setup.sh
Source7:          nss-softokn-dracut.conf
Source8:          nss.pc.in
Source9:          nss-config.in
Source10:         blank-cert8.db
Source11:         blank-key3.db
Source12:         blank-secmod.db
Source13:         blank-cert9.db
Source14:         blank-key4.db
Source15:         system-pkcs11.txt
Source16:         setup-nsssysinit.sh
Source20:         nss-config.xml
Source21:         setup-nsssysinit.xml
Source22:         pkcs11.txt.xml
Source23:         cert8.db.xml
Source24:         cert9.db.xml
Source25:         key3.db.xml
Source26:         key4.db.xml
Source27:         secmod.db.xml	
Source28:         nss-p11-kit.config


Patch2:           add-relro-linker-option.patch
Patch3:           renegotiate-transitional.patch
Patch8:           nss-sysinit-userdb-first.patch
# Upstream: https://bugzilla.mozilla.org/show_bug.cgi?id=617723
Patch16:          nss-539183.patch
# TODO remove when we switch to building nss without softoken
Patch49:          nss-skip-bltest-and-fipstest.patch
# This patch uses the GCC -iquote option documented at
# http://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html#Directory-Options
# to give the in-tree headers a higher priority over the system headers,
# when they are included through the quote form (#include "file.h").
#
# This ensures a build even when system headers are older. Such is the
# case when starting an update with API changes or even private export
# changes.
#
# Once the buildroot aha been bootstrapped the patch may be removed
# but it doesn't hurt to keep it.
Patch50:          iquote.patch
# Local patch for TLS_ECDHE_{ECDSA|RSA}_WITH_3DES_EDE_CBC_SHA ciphers
Patch58:          rhbz1185708-enable-ecc-3des-ciphers-by-default.patch
Patch62:          nss-skip-util-gtest.patch

%description
Network Security Services (NSS) is a set of libraries designed to
support cross-platform development of security-enabled client and
server applications. Applications built with NSS can support SSL v2
and v3, TLS, PKCS #5, PKCS #7, PKCS #11, PKCS #12, S/MIME, X.509
v3 certificates, and other security standards.

%package tools
Summary:          Tools for the Network Security Services
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description tools
Network Security Services (NSS) is a set of libraries designed to
support cross-platform development of security-enabled client and
server applications. Applications built with NSS can support SSL v2
and v3, TLS, PKCS #5, PKCS #7, PKCS #11, PKCS #12, S/MIME, X.509
v3 certificates, and other security standards.

Install the nss-tools package if you need command-line tools to
manipulate the NSS certificate and key database.

%package sysinit
Summary:          System NSS Initialization
# providing nss-system-init without version so that it can
# be replaced by a better one, e.g. supplied by the os vendor
Provides:         nss-system-init
Requires:         nss = %{version}-%{release}
Requires(post):   coreutils, sed

%description sysinit
Default Operating System module that manages applications loading
NSS globally on the system. This module loads the system defined
PKCS #11 modules for NSS and chains with other NSS modules to load
any system or user configured modules.

%package devel
Summary:          Development libraries for Network Security Services
Provides:         nss-static = %{version}-%{release}
Requires:         nss = %{version}-%{release}
Requires:         nspr-devel >= %{nspr_version}
Requires:         pkgconfig

%description devel
Header and Library files for doing development with Network Security Services.

%package pkcs11-devel
Summary:          Development libraries for PKCS 11 (Cryptoki) using NSS
Provides:         nss-pkcs11-devel-static = %{version}-%{release}
Requires:         nss-devel = %{version}-%{release}
Requires:         nss-softokn-freebl-devel >= %{version}

%description pkcs11-devel
Library files for developing PKCS #11 modules using basic NSS
low level services.

%package util
Summary:          Network Security Services Utilities Library
Requires:         nspr >= %{nspr_version}
	
%description util
Utilities for Network Security Services and the Softoken module
	
%package util-devel
Summary:          Development libraries for Network Security Services Utilities
Requires:         nss-util%{?_isa} = %{version}-%{release}
Requires:         nspr-devel >= %{nspr_version}
Requires:         pkgconfig
 
%description util-devel
Header and library files for doing development with Network Security Services.

%package softokn
Summary:          Network Security Services Softoken Module
Requires:         nspr >= %{nspr_version}
Requires:         nss-util >= %{version}-%{release}
Requires:         nss-softokn-freebl%{_isa} >= %{version}-%{release}
	
%description softokn
Network Security Services Softoken Cryptographic Module. Softoken is an NSS 
module that exposes most FreeBL functionality as a PKCS#11 module.
 
%package softokn-freebl
Summary:          Freebl library for the Network Security Services
# For PR_GetEnvSecure() from nspr >= 4.12
Requires:         nspr >= 4.12
# For NSS_SecureMemcmpZero() from nss-util >= 3.33
Requires:         nss-util >= 3.33
Conflicts:        nss < 3.12.2.99.3-5
Conflicts:        filesystem < 3

%description softokn-freebl
FreeBL Cryptographic Module, a base library providing hash functions, 
big number calculations, and cryptographic algorithms.

%package softokn-freebl-devel
Summary:          Development files for Softoken Freebl libraries for NSS
Provides:         nss-softokn-freebl-static = %{version}-%{release}
Requires:         nss-softokn-freebl%{?_isa} = %{version}-%{release}

%description softokn-freebl-devel
NSS Softoken Cryptographic Module FreeBL Library Development Tools
This package supports special needs of some PKCS #11 module developers and
is otherwise considered private to NSS. As such, the programming interfaces
may change and the usual NSS binary compatibility commitments do not apply.
Developers should rely only on the officially supported NSS public API.
	
%package softokn-devel
Summary:          Development libraries for Network Security Services
Requires:         nss-softokn%{?_isa} = %{version}-%{release}
Requires:         nss-softokn-freebl-devel%{?_isa} = %{version}-%{release}
Requires:         nspr-devel >= %{nspr_version}
Requires:         nss-util-devel >= %{version}-%{release}
Requires:         pkgconfig
BuildRequires:    nspr-devel >= %{nspr_version}
	
%description softokn-devel
Header and library files for doing development with Network Security Services.

%prep
%setup -q -n %{name}-%{version}/%{name}

%patch2 -p1 -b .relro
%patch3 -p1 -b .transitional
%patch8 -p2 -b .sysinit_userdb
%patch16 -p2 -b .539183
%patch49 -p2 -b .skip_bltest
%patch50 -p1 -b .iquote
%patch58 -p2 -b .1185708_3des
%patch62 -p1 -b .skip_util_gtest


%build
# TODO: new build system with gyp & ninja

export FREEBL_NO_DEPEND=1

# Must export FREEBL_LOWHASH=1 for nsslowhash.h so that it gets
# copied to dist and the rpm install phase can find it
# This due of the upstream changes to fix
# https://bugzilla.mozilla.org/show_bug.cgi?id=717906
export FREEBL_LOWHASH=1

# Enable FIPS startup test
export NSS_FORCE_FIPS=1

# Enable compiler optimizations and disable debugging code
export BUILD_OPT=1

# Uncomment to disable optimizations
#RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/-O2/-O0/g'`
#export RPM_OPT_FLAGS

# Generate symbolic info for debuggers
export XCFLAGS=$RPM_OPT_FLAGS

export LDFLAGS=$RPM_LD_FLAGS

export PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
export NSPR_LIB_DIR=%{_libdir}

export NSS_USE_SYSTEM_SQLITE=1

export USE_SYSTEM_ZLIB=1
export ZLIB_LIBS=-lz

#export NSS_ALLOW_SSLKEYLOGFILE=1

export NSS_DISABLE_GTESTS=1

%ifnarch noarch
%if 0%{__isa_bits} == 64
export USE_64=1
%endif
%endif

# uncomment if the iquote patch is activated
export IN_TREE_FREEBL_HEADERS_FIRST=1

##### phase 2: build the rest of nss

# Set the policy file location
# if set NSS will always check for the policy file and load if it exists
export POLICY_FILE="nss.config"
# location of the policy file
export POLICY_PATH="/etc/crypto-policies/back-ends"

%{__make} all
%{__make} latest

# This will copy to dist dir and sign libraries
%{__make} install


# Disable man pages, since make dont find xmlto command.
# build the man pages clean
#pushd ./nss
#{__make} clean_docs build_docs
#popd

# and copy them to the dist directory for %%install to find them
#mkdir -p ./dist/docs/nroff
#cp ./nss/doc/nroff/* ./dist/docs/nroff

# Set up our package files
mkdir -p ../dist/pkgconfig
	
cat %{SOURCE1} | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/nss3,g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSSUTIL_VERSION%%,%{version},g" > \
                          ../dist/pkgconfig/nss-util.pc
	
NSSUTIL_VMAJOR=`cat lib/util/nssutil.h | grep "#define.*NSSUTIL_VMAJOR" | awk '{print $3}'`
NSSUTIL_VMINOR=`cat lib/util/nssutil.h | grep "#define.*NSSUTIL_VMINOR" | awk '{print $3}'`
NSSUTIL_VPATCH=`cat lib/util/nssutil.h | grep "#define.*NSSUTIL_VPATCH" | awk '{print $3}'`

export NSSUTIL_VMAJOR
export NSSUTIL_VMINOR
export NSSUTIL_VPATCH	
 
cat %{SOURCE2} | sed -e "s,@libdir@,%{_libdir},g" \
                          -e "s,@prefix@,%{_prefix},g" \
                          -e "s,@exec_prefix@,%{_prefix},g" \
                          -e "s,@includedir@,%{_includedir}/nss3,g" \
                          -e "s,@MOD_MAJOR_VERSION@,$NSSUTIL_VMAJOR,g" \
                          -e "s,@MOD_MINOR_VERSION@,$NSSUTIL_VMINOR,g" \
                          -e "s,@MOD_PATCH_VERSION@,$NSSUTIL_VPATCH,g" \
                          > ../dist/pkgconfig/nss-util-config
	
chmod 755 ../dist/pkgconfig/nss-util-config
	
cat %{SOURCE3} | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/nss3,g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSSUTIL_VERSION%%,%{version},g" \
                          -e "s,%%SOFTOKEN_VERSION%%,%{version},g" > \
                          ../dist/pkgconfig/nss-softokn.pc
	
SOFTOKEN_VMAJOR=`cat lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMAJOR" | awk '{print $3}'`
SOFTOKEN_VMINOR=`cat lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMINOR" | awk '{print $3}'`
SOFTOKEN_VPATCH=`cat lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VPATCH" | awk '{print $3}'`

export SOFTOKEN_VMAJOR
export SOFTOKEN_VMINOR
export SOFTOKEN_VPATCH	
 
cat %{SOURCE4} | sed -e "s,@libdir@,%{_libdir},g" \
                          -e "s,@prefix@,%{_prefix},g" \
                          -e "s,@exec_prefix@,%{_prefix},g" \
                          -e "s,@includedir@,%{_includedir}/nss3,g" \
                          -e "s,@MOD_MAJOR_VERSION@,$SOFTOKEN_VMAJOR,g" \
                          -e "s,@MOD_MINOR_VERSION@,$SOFTOKEN_VMINOR,g" \
                          -e "s,@MOD_PATCH_VERSION@,$SOFTOKEN_VPATCH,g" \
                          > ../dist/pkgconfig/nss-softokn-config
 
chmod 755 ../dist/pkgconfig/nss-softokn-config
	
cat %{SOURCE8} | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/nss3,g" \
                          -e "s,%%NSS_VERSION%%,%{version},g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSSUTIL_VERSION%%,%{version},g" \
                          -e "s,%%SOFTOKEN_VERSION%%,%{version},g" > \
                          ../dist/pkgconfig/nss.pc
	
NSS_VMAJOR=`cat lib/nss/nss.h | grep "#define.*NSS_VMAJOR" | awk '{print $3}'`
NSS_VMINOR=`cat lib/nss/nss.h | grep "#define.*NSS_VMINOR" | awk '{print $3}'`
NSS_VPATCH=`cat lib/nss/nss.h | grep "#define.*NSS_VPATCH" | awk '{print $3}'`

export NSS_VMAJOR
export NSS_VMINOR
export NSS_VPATCH	
 	
cat %{SOURCE9} | sed -e "s,@libdir@,%{_libdir},g" \
                          -e "s,@prefix@,%{_prefix},g" \
                          -e "s,@exec_prefix@,%{_prefix},g" \
                          -e "s,@includedir@,%{_includedir}/nss3,g" \
                          -e "s,@MOD_MAJOR_VERSION@,$NSS_VMAJOR,g" \
                          -e "s,@MOD_MINOR_VERSION@,$NSS_VMINOR,g" \
                          -e "s,@MOD_PATCH_VERSION@,$NSS_VPATCH,g" \
                          > ../dist/pkgconfig/nss-config
	
chmod 755 ../dist/pkgconfig/nss-config

cat %{SOURCE16} > ../dist/pkgconfig/setup-nsssysinit.sh
chmod 755 ../dist/pkgconfig/setup-nsssysinit.sh

cp lib/ckfw/nssck.api ../dist/private/nss/

date +"%e %B %Y" | tr -d '\n' > date.xml
echo -n %{version} > version.xml

%check
if [ ${DISABLETEST:-0} -eq 1 ]; then
  echo "testing disabled"
  exit 0
fi

# Begin -- copied from the build section

FREEBL_NO_DEPEND=1
export FREEBL_NO_DEPEND

export BUILD_OPT=1

%ifnarch noarch
%if 0%{__isa_bits} == 64
USE_64=1
export USE_64
%endif
%endif

export NSS_BLTEST_NOT_AVAILABLE=1

# needed for the fips mangling test
export SOFTOKEN_LIB_DIR=%{_libdir}

# End -- copied from the build section

# This is necessary because the test suite tests algorithms that are
# disabled by the system policy.
export NSS_IGNORE_SYSTEM_POLICY=1

# enable the following line to force a test failure
# find ./nss -name \*.chk | xargs rm -f

# Run test suite.
# In order to support multiple concurrent executions of the test suite
# (caused by concurrent RPM builds) on a single host,
# we'll use a random port. Also, we want to clean up any stuck
# selfserv processes. If process name "selfserv" is used everywhere,
# we can't simply do a "killall selfserv", because it could disturb
# concurrent builds. Therefore we'll do a search and replace and use
# a different process name.
# Using xargs doesn't mix well with spaces in filenames, in order to
# avoid weird quoting we'll require that no spaces are being used.

SPACEISBAD=`find tests | grep -c ' '` ||:
if [ $SPACEISBAD -ne 0 ]; then
  echo "error: filenames containing space are not supported (xargs)"
  exit 1
fi
MYRAND=`perl -e 'print 9000 + int rand 1000'`; echo $MYRAND ||:
RANDSERV=selfserv_${MYRAND}; echo $RANDSERV ||:
DISTBINDIR=`ls -d ../dist/*.OBJ/bin`; echo $DISTBINDIR ||:
pushd `pwd`
cd $DISTBINDIR
ln -s selfserv $RANDSERV
popd
# man perlrun, man perlrequick
# replace word-occurrences of selfserv with selfserv_$MYRAND
find tests -type f |\
  grep -v "\.db$" |grep -v "\.crl$" | grep -v "\.crt$" |\
  grep -vw CVS  |xargs grep -lw selfserv |\
  xargs -L 1 perl -pi -e "s/\bselfserv\b/$RANDSERV/g" ||:

killall $RANDSERV || :

rm -rf ./tests_results
pushd tests/
# all.sh is the test suite script

#  don't need to run all the tests when testing packaging
#  nss_cycles: standard pkix upgradedb sharedb
#  the full list from all.sh is:
#  "cipher lowhash libpkix cert dbtests tools fips sdr crmf smime ssl ocsp merge pkits chains ec gtests ssl_gtests"
%define nss_tests "libpkix cert dbtests tools fips sdr crmf smime ssl ocsp merge pkits chains ec gtests ssl_gtests"
#  nss_ssl_tests: crl bypass_normal normal_bypass normal_fips fips_normal iopr policy
#  nss_ssl_run: cov auth stapling stress
#
# Uncomment these lines if you need to temporarily
# disable some test suites for faster test builds
# % define nss_ssl_tests "normal_fips"
# % define nss_ssl_run "cov"

SKIP_NSS_TEST_SUITE=1

if [ "x$SKIP_NSS_TEST_SUITE" == "x" ]; then
  HOST=localhost DOMSUF=localdomain PORT=$MYRAND NSS_CYCLES=%{?nss_cycles} NSS_TESTS=%{?nss_tests} NSS_SSL_TESTS=%{?nss_ssl_tests} NSS_SSL_RUN=%{?nss_ssl_run} ./all.sh
else
  echo "skipped test suite"
fi
popd

# Normally, the grep exit status is 0 if selected lines are found and 1 otherwise,
# Grep exits with status greater than 1 if an error ocurred.
# If there are test failures we expect TEST_FAILURES > 0 and GREP_EXIT_STATUS = 0,
# With no test failures we expect TEST_FAILURES = 0 and GREP_EXIT_STATUS = 1, whereas
# GREP_EXIT_STATUS > 1 would indicate an error in grep such as failure to find the log file.
killall $RANDSERV || :

if [ "x$SKIP_NSS_TEST_SUITE" == "x" ]; then
  TEST_FAILURES=$(grep -c -- '- FAILED$' ./tests_results/security/localhost.1/output.log) || GREP_EXIT_STATUS=$?
else
  TEST_FAILURES=0
  GREP_EXIT_STATUS=1
fi

if [ ${GREP_EXIT_STATUS:-0} -eq 1 ]; then
  echo "okay: test suite detected no failures"
else
  if [ ${GREP_EXIT_STATUS:-0} -eq 0 ]; then
    # while a situation in which grep return status is 0 and it doesn't output
    # anything shouldn't happen, set the default to something that is
    # obviously wrong (-1)
    echo "error: test suite had ${TEST_FAILURES:--1} test failure(s)"
    exit 1
  else
    if [ ${GREP_EXIT_STATUS:-0} -eq 2 ]; then
      echo "error: grep has not found log file"
      exit 1
    else
      echo "error: grep failed with exit code: ${GREP_EXIT_STATUS}"
      exit 1
    fi
  fi
fi
echo "test suite completed"

%install
%{__rm} -rf $RPM_BUILD_ROOT

# There is no make install target so we'll do it ourselves.

%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/nss3
%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/nss3/templates
%{__mkdir_p} $RPM_BUILD_ROOT/%{_bindir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{unsupported_tools_directory}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%{__mkdir_p} $RPM_BUILD_ROOT/%{saved_files_dir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{dracut_modules_dir}	
%{__mkdir_p} $RPM_BUILD_ROOT/%{dracut_conf_dir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}/crypto-policies/local.d
# because of the pp.1 conflict with perl-PAR-Packer
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/doc/nss-tools

install -m 755 %{SOURCE6} $RPM_BUILD_ROOT/%{dracut_modules_dir}/module-setup.sh
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT/%{dracut_conf_dir}/50-nss-softokn.conf

# Copy the binary libraries we want
for file in libnss3.so libnsssysinit.so libsmime3.so libssl3.so libsoftokn3.so libsoftokn3.chk libnssdbm3.so libnssdbm3.chk libfreebl3.so libfreebl3.chk libfreeblpriv3.so libfreeblpriv3.chk libnssutil3.so
do
  %{__install} -p -m 755 ../dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Install the empty NSS db files
# Legacy db
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb
%{__install} -p -m 644 %{SOURCE10} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/cert8.db
%{__install} -p -m 644 %{SOURCE11} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/key3.db
%{__install} -p -m 644 %{SOURCE12} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/secmod.db
# Shared db
%{__install} -p -m 644 %{SOURCE13} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/cert9.db
%{__install} -p -m 644 %{SOURCE14} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/key4.db
%{__install} -p -m 644 %{SOURCE15} $RPM_BUILD_ROOT/%{_sysconfdir}/pki/nssdb/pkcs11.txt

# Copy the development libraries we want
for file in libcrmf.a libnssb.a libnssckfw.a
do
  %{__install} -p -m 644 ../dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Copy the binaries we want
for file in certutil cmsutil crlutil modutil nss-policy-check pk12util signver ssltap
do
  %{__install} -p -m 755 ../dist/*.OBJ/bin/$file $RPM_BUILD_ROOT/%{_bindir}
done

# Copy the binaries we ship as unsupported
for file in atob btoa derdump listsuites ocspclnt pp selfserv signtool strsclnt symkeyutil tstclnt vfyserv vfychain bltest ecperf fbectest fipstest shlibsign
do
  %{__install} -p -m 755 ../dist/*.OBJ/bin/$file $RPM_BUILD_ROOT/%{unsupported_tools_directory}
done

# Copy the include files we want
for file in ../dist/public/nss/*.h
do
  %{__install} -p -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy some freebl include files we also want
for file in blapi.h alghmac.h cmac.h
do
  %{__install} -p -m 644 ../dist/private/nss/$file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy the static freebl library
for file in libfreebl.a
do
%{__install} -p -m 644 ../dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Copy the template files we want
for file in ../dist/private/nss/nssck.api
do
  %{__install} -p -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/nss3/templates
done
for file in ../dist/private/nss/templates.c ../dist/private/nss/nssck.api
do
  %{__install} -p -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/nss3/templates
done

# Copy the package configuration files
%{__install} -p -m 644 ../dist/pkgconfig/nss.pc $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nss.pc
%{__install} -p -m 644 ../dist/pkgconfig/nss-softokn.pc $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nss-softokn.pc
%{__install} -p -m 755 ../dist/pkgconfig/nss-softokn-config $RPM_BUILD_ROOT/%{_bindir}/nss-softokn-config
%{__install} -p -m 644 ../dist/pkgconfig/nss-util.pc $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nss-util.pc
%{__install} -p -m 755 ../dist/pkgconfig/nss-util-config $RPM_BUILD_ROOT/%{_bindir}/nss-util-config
%{__install} -p -m 755 ../dist/pkgconfig/nss-config $RPM_BUILD_ROOT/%{_bindir}/nss-config

# Copy the pkcs #11 configuration script
%{__install} -p -m 755 ../dist/pkgconfig/setup-nsssysinit.sh $RPM_BUILD_ROOT/%{_bindir}/setup-nsssysinit.sh
# install a symbolic link to it, without the ".sh" suffix,
# that matches the man page documentation
ln -s -f setup-nsssysinit.sh $RPM_BUILD_ROOT/%{_bindir}/setup-nsssysinit

# Copy the crypto-policies configuration file
	
%{__install} -p -m 644 %{SOURCE28} $RPM_BUILD_ROOT/%{_sysconfdir}/crypto-policies/local.d

%triggerpostun -n nss-sysinit -- nss-sysinit < 3.12.8-3
# Reverse unwanted disabling of sysinit by faulty preun sysinit scriplet
# from previous versions of nss.spec
/usr/bin/setup-nsssysinit.sh on

%ldconfig_scriptlets

%post
update-crypto-policies &> /dev/null || :
	
%postun	
update-crypto-policies &> /dev/null || :

%files
%license ../nss/COPYING
%{_libdir}/libnss3.so
%{_libdir}/libssl3.so
%{_libdir}/libsmime3.so
%dir %{_sysconfdir}/pki/nssdb
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/cert8.db
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/key3.db
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/secmod.db
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/cert9.db
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/key4.db
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/nssdb/pkcs11.txt
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/crypto-policies/local.d/nss-p11-kit.config
%dir %{unsupported_tools_directory}
%{unsupported_tools_directory}/shlibsign

%files sysinit
%{_libdir}/libnsssysinit.so
%{_bindir}/setup-nsssysinit.sh
# symbolic link to setup-nsssysinit.sh
%{_bindir}/setup-nsssysinit

%files tools
%{_bindir}/certutil
%{_bindir}/cmsutil
%{_bindir}/crlutil
%{_bindir}/modutil
%{_bindir}/nss-policy-check
%{_bindir}/pk12util
%{_bindir}/signver
%{_bindir}/ssltap
%{unsupported_tools_directory}/atob
%{unsupported_tools_directory}/btoa
%{unsupported_tools_directory}/derdump
%{unsupported_tools_directory}/listsuites
%{unsupported_tools_directory}/ocspclnt
%{unsupported_tools_directory}/pp
%{unsupported_tools_directory}/selfserv
%{unsupported_tools_directory}/signtool
%{unsupported_tools_directory}/strsclnt
%{unsupported_tools_directory}/symkeyutil
%{unsupported_tools_directory}/tstclnt
%{unsupported_tools_directory}/vfyserv
%{unsupported_tools_directory}/vfychain

%files devel
%{_libdir}/libcrmf.a
%{_libdir}/pkgconfig/nss.pc
%{_bindir}/nss-config
%dir %{_includedir}/nss3
%{_includedir}/nss3/cert.h
%{_includedir}/nss3/certdb.h
%{_includedir}/nss3/certt.h
%{_includedir}/nss3/cmmf.h
%{_includedir}/nss3/cmmft.h
%{_includedir}/nss3/cms.h
%{_includedir}/nss3/cmsreclist.h
%{_includedir}/nss3/cmst.h
%{_includedir}/nss3/crmf.h
%{_includedir}/nss3/crmft.h
%{_includedir}/nss3/cryptohi.h
%{_includedir}/nss3/cryptoht.h
%{_includedir}/nss3/sechash.h
%{_includedir}/nss3/jar-ds.h
%{_includedir}/nss3/jar.h
%{_includedir}/nss3/jarfile.h
%{_includedir}/nss3/key.h
%{_includedir}/nss3/keyhi.h
%{_includedir}/nss3/keyt.h
%{_includedir}/nss3/keythi.h
%{_includedir}/nss3/nss.h
%{_includedir}/nss3/nssckbi.h
%{_includedir}/nss3/ocsp.h
%{_includedir}/nss3/ocspt.h
%{_includedir}/nss3/p12.h
%{_includedir}/nss3/p12plcy.h
%{_includedir}/nss3/p12t.h
%{_includedir}/nss3/pk11func.h
%{_includedir}/nss3/pk11hpke.h
%{_includedir}/nss3/pk11pqg.h
%{_includedir}/nss3/pk11priv.h
%{_includedir}/nss3/pk11pub.h
%{_includedir}/nss3/pk11sdr.h
%{_includedir}/nss3/pkcs12.h
%{_includedir}/nss3/pkcs12t.h
%{_includedir}/nss3/pkcs7t.h
%{_includedir}/nss3/preenc.h
%{_includedir}/nss3/secmime.h
%{_includedir}/nss3/secmod.h
%{_includedir}/nss3/secmodt.h
%{_includedir}/nss3/secpkcs5.h
%{_includedir}/nss3/secpkcs7.h
%{_includedir}/nss3/smime.h
%{_includedir}/nss3/ssl.h
%{_includedir}/nss3/sslerr.h
%{_includedir}/nss3/sslexp.h
%{_includedir}/nss3/sslproto.h
%{_includedir}/nss3/sslt.h
%{_includedir}/nss3/blapit.h
%{_includedir}/nss3/ecl-exp.h
%{_libdir}/pkgconfig/nss-util.pc
%{_includedir}/nss3/base64.h
%{_includedir}/nss3/ciferfam.h
%{_includedir}/nss3/eccutil.h
%{_includedir}/nss3/hasht.h
%{_includedir}/nss3/nssb64.h
%{_includedir}/nss3/nssb64t.h
%{_includedir}/nss3/nsslocks.h
%{_includedir}/nss3/nssilock.h
%{_includedir}/nss3/nssilckt.h
%{_includedir}/nss3/nssrwlk.h
%{_includedir}/nss3/nssrwlkt.h
%{_includedir}/nss3/nssutil.h
%{_includedir}/nss3/pkcs1sig.h
%{_includedir}/nss3/pkcs11.h
%{_includedir}/nss3/pkcs11f.h
%{_includedir}/nss3/pkcs11n.h
%{_includedir}/nss3/pkcs11p.h
%{_includedir}/nss3/pkcs11t.h
%{_includedir}/nss3/pkcs11u.h
%{_includedir}/nss3/pkcs11uri.h
%{_includedir}/nss3/portreg.h
%{_includedir}/nss3/secasn1.h
%{_includedir}/nss3/secasn1t.h
%{_includedir}/nss3/seccomon.h
%{_includedir}/nss3/secder.h
%{_includedir}/nss3/secdert.h
%{_includedir}/nss3/secdig.h
%{_includedir}/nss3/secdigt.h
%{_includedir}/nss3/secerr.h
%{_includedir}/nss3/secitem.h
%{_includedir}/nss3/secoid.h
%{_includedir}/nss3/secoidt.h
%{_includedir}/nss3/secport.h
%{_includedir}/nss3/utilmodt.h
%{_includedir}/nss3/utilpars.h
%{_includedir}/nss3/utilparst.h
%{_includedir}/nss3/utilrename.h
%{_includedir}/nss3/templates/templates.c

%files pkcs11-devel
%{_includedir}/nss3/nssbase.h
%{_includedir}/nss3/nssbaset.h
%{_includedir}/nss3/nssckepv.h
%{_includedir}/nss3/nssckft.h
%{_includedir}/nss3/nssckfw.h
%{_includedir}/nss3/nssckfwc.h
%{_includedir}/nss3/nssckfwt.h
%{_includedir}/nss3/nssckg.h
%{_includedir}/nss3/nssckmdt.h
%{_includedir}/nss3/nssckt.h
%{_includedir}/nss3/templates/nssck.api
%{_libdir}/libnssb.a
%{_libdir}/libnssckfw.a

%files util
%{!?_licensedir:%global license %%doc}
%license ../nss/COPYING
%{_libdir}/libnssutil3.so
 
%files util-devel
# package configuration files
%{_libdir}/pkgconfig/nss-util.pc
%{_bindir}/nss-util-config
# co-owned with nss
%dir %{_includedir}/nss3
# these are marked as public export in nss/lib/util/manifest.mk
%{_includedir}/nss3/base64.h
%{_includedir}/nss3/ciferfam.h
%{_includedir}/nss3/eccutil.h
%{_includedir}/nss3/hasht.h
%{_includedir}/nss3/nssb64.h
%{_includedir}/nss3/nssb64t.h
%{_includedir}/nss3/nsslocks.h
%{_includedir}/nss3/nssilock.h
%{_includedir}/nss3/nssilckt.h
%{_includedir}/nss3/nssrwlk.h
%{_includedir}/nss3/nssrwlkt.h
%{_includedir}/nss3/nssutil.h
%{_includedir}/nss3/pkcs1sig.h
%{_includedir}/nss3/pkcs11.h
%{_includedir}/nss3/pkcs11f.h
%{_includedir}/nss3/pkcs11n.h
%{_includedir}/nss3/pkcs11p.h
%{_includedir}/nss3/pkcs11t.h
%{_includedir}/nss3/pkcs11u.h
%{_includedir}/nss3/pkcs11uri.h
%{_includedir}/nss3/portreg.h
%{_includedir}/nss3/secasn1.h
%{_includedir}/nss3/secasn1t.h
%{_includedir}/nss3/seccomon.h
%{_includedir}/nss3/secder.h
%{_includedir}/nss3/secdert.h
%{_includedir}/nss3/secdig.h
%{_includedir}/nss3/secdigt.h
%{_includedir}/nss3/secerr.h
%{_includedir}/nss3/secitem.h
%{_includedir}/nss3/secoid.h
%{_includedir}/nss3/secoidt.h
%{_includedir}/nss3/secport.h
%{_includedir}/nss3/utilmodt.h
%{_includedir}/nss3/utilpars.h
%{_includedir}/nss3/utilparst.h
%{_includedir}/nss3/utilrename.h
%{_includedir}/nss3/templates/templates.c

%files softokn
%{_libdir}/libnssdbm3.so	
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.so
%{_libdir}/libsoftokn3.chk
# shared with nss-tools
%dir %{_libdir}/nss
%dir %{saved_files_dir}
%dir %{unsupported_tools_directory}
%{unsupported_tools_directory}/bltest
%{unsupported_tools_directory}/ecperf
%{unsupported_tools_directory}/fbectest
%{unsupported_tools_directory}/fipstest
%{unsupported_tools_directory}/shlibsign

%files softokn-freebl
%{!?_licensedir:%global license %%doc}
%license ../nss/COPYING
%{_libdir}/libfreebl3.so
%{_libdir}/libfreebl3.chk
%{_libdir}/libfreeblpriv3.so
%{_libdir}/libfreeblpriv3.chk
#shared
%dir %{dracut_modules_dir}
%{dracut_modules_dir}/module-setup.sh
%{dracut_conf_dir}/50-nss-softokn.conf

%files softokn-freebl-devel
%{_libdir}/libfreebl.a
%{_includedir}/nss3/blapi.h
%{_includedir}/nss3/blapit.h
%{_includedir}/nss3/alghmac.h
%{_includedir}/nss3/cmac.h
%{_includedir}/nss3/lowkeyi.h
%{_includedir}/nss3/lowkeyti.h
	
%files softokn-devel
%{_libdir}/pkgconfig/nss-softokn.pc
%{_bindir}/nss-softokn-config
# co-owned with nss
%dir %{_includedir}/nss3
#
# The following headers are those exported public in
# nss/lib/freebl/manifest.mn and
# nss/lib/softoken/manifest.mn
#
# The following list is short because many headers, such as
# the pkcs #11 ones, have been provided by nss-util-devel
# which installed them before us.
#
%{_includedir}/nss3/ecl-exp.h
%{_includedir}/nss3/nsslowhash.h
%{_includedir}/nss3/shsign.h

