#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"

# Defaults
 if [ -n "$1" ] ; then
    CODE_VARIANT="$1"
 fi
 if [ -n "$2" ] ; then
    AASIGDP_TARGET="$2"
 fi


#PROJDIR=/workdir
PROJDIR=$PWD/..

#PROJDIR=/workdir
PROJDIR=$PWD/..

# According to https://source.android.com/setup/build/downloading
REPO_SHA=d73f3885d717c1dc89eba0563433cec787486a0089b9b04b4e8c56e7c07c7610

# LOG helpers
section() {
  echo '========================================================================='
  echo "init.sh, section: $1"
  echo '========================================================================='
}

# Helper functiosn
fail_target() {
    echo "Unknown target ($AASIGDP_TARGET).  Please make sure variable \$AASIGDP_TARGET is set to a known value."
    exit 1
}

required_file() {
  local d="$PWD"
  cd "$PROJDIR"  # files specified relative to root of project
  if [ -f "$1" ] ; then
    echo "Found: $1"
  else
    failed_prereqs="$1 $failed_prereqs"
  fi
  cd "$d"
}

check_required_files_result() {
  if [ -n "$failed_prereqs" ] ; then
    echo "To continue, the following vendor specific files must be provided.   Please consult the documentation/README for how to get them"
    echo " --> $failed_prereqs"
    exit 2
  else
    echo "Seems OK"
  fi
}

# Set up any unique for initial repo init (or fail early if target not defined)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    section "Set repo manifest, url, branch, flags ($AASIGDP_TARGET)"
    manifest="-m imx-p9.0.0_2.3.0.xml"
    url=https://source.codeaurora.org/external/imx/imx-manifest.git
    branch=imx-android-pie
    flags=
    ;;

  # RENESAS R-Car H3 or M3 starter-kit, same steps:
  ?3ulcb)
    section "Unset manifest/url/branch/flags ($AASIGDP_TARGET) because it is handled by delegate scripts"
    # This is all controlled by the provided RENESAS scripts
    manifest=
    url=
    branch=
    flags=
    section "Check main BSP file exists ($AASIGDP_TARGET)"
    outer_zip_name=REE-EG_Android-10-2020_03E-v10_1.2_H3
    inner_zip_name=RENESAS_RCH3M3M3N_Android_10_ReleaseNote_2020_03E
    required_file "vendor/renesas/$outer_zip_name.zip"

    # Link the unique build results path for convenience
    section "Create build_result symlink ($AASIGDP_TARGET)"
    rm -f "$PROJDIR/build_result"  # (if exists)
    ln -s "$PROJDIR/vendor/renesas/$outer_zip_name/source/bsp/$inner_zip_name/mydroid/out/target/product/kingfisher" "$PROJDIR/build_result"
    ;;

  hikey960)
    section "TBD ($AASIGDP_TARGET)"
    # According to: https://source.android.com/setup/build/devices (Checked 2020-09)
    url=https://android.googlesource.com/platform/manifest
    branch=master
    manifest=""  # (use default)
    flags=
    ;;

  hikey970)
    section "TBD ($AASIGDP_TARGET)"
    echo UNTESTED
    # According to https://github.com/96boards/documentation/wiki
    url=https://android.googlesource.com/platform/manifest
    branch=android-9.0.0_r8
    flags="--no-repo-verify --repo-branch=stable"
    ;;

  *)
    section "*** ERROR ***"
    fail_target
    ;;
esac

check_required_files_result
failed_prereqs=

section "Get & check initial repo binary from Google"
cd "$PROJDIR/bin"
curl https://storage.googleapis.com/git-repo-downloads/repo > ./repo
chmod a+x ./repo

sha256sum </dev/null >/dev/null || echo "Could not run sha256sum??"
if [ "$(sha256sum ./repo | cut -c 1-64)" != "$REPO_SHA" ] ; then
  echo "Hash mismatch -> repo version was updated?  Check it before running..."
  echo "Expected: $REPO_HASH"
  echo -n "Got: " ; sha256sum repo
  echo "You might check https://source.android.com/setup/build/downloading for update"
fi

section "git config user name/email"
git config user.name 2>/dev/null
# failed?  If so, configure the username
if [ $? -ne 0 ] ; then
   echo "A git user name and email must be configured for later build steps"
   echo "You seem to be running outside of container, because the container should have it configured already."
   echo "Therefore, please note that what you provide here will be stored in the global git settings (in your home directory!)"
   read -p "Name:"  name
   read -p "Email:" email

   git config --global user.name  "$name"
   git config --global user.email "$email"
fi

section "repo init"
if [ -n "$url" ] ; then
   cd "$PROJDIR"
   bin/repo init -u $url -b $branch $manifest

   # After repo init there will be a new(er) repo version in .repo/ ...
   # Update repo command from this local copy to avoid nagging warnings
   # (Note, on some platforms using SELinux, manipulating binaries
   # like this might possibly fail)
   if [ -f .repo/repo/repo ] ; then
      echo "Copying locally initialized repo command to $(readlink -f ../bin/) to make sure it is up to date."
      cp .repo/repo/repo ../bin/repo
      chmod 755 ../bin/repo
   fi
else
   echo "Repo url is unset => no init at this time"
fi

# Continue with additional steps for init
cd "$PROJDIR"
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    ;;
  # RENESAS R-Car H3 starter-kit
  h3ulcb)
  section "Unpack and check all BSP files ($AASIGDP_TARGET)"
    cd $PROJDIR/vendor/renesas
    pkg="$outer_zip_name.zip" # REE-EG_Android-<version>...etc.
    echo "Unpacking $pkg"
    unzip -o "$pkg"

    # Sanity check results:

    failed_prereqs=
    # inner_zip_name = RENESAS_RCH3M3M3N_Android_<version>_ReleaseNote_...
    required_file "vendor/renesas/$outer_zip_name/source/bsp/$inner_zip_name.zip"
    check_required_files_result

    # For H3:
    failed_prereqs=

    required_file "vendor/renesas/$outer_zip_name/source/proprietary/gfx/RCH3G001A1001ZDO_1_0_2.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/gfx/RTM8RC7795ZGG00Q00JPAQE_1_0_2.zip"
    #For M3: RCM3G001A1001ZDO_1_0_2.zip
    #For M3: RTM8RC7796ZGG00Q00JPAQE_1_0_2.zip
    #For M3N: RCN3G001A1001ZDO_1_0_2.zip
    #For M3N: RTM8RC7796ZGG00Q50JPAQE_1_0_2.zip

    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD0LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD1LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD2LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD3LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD4LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD8LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMD9LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMDALQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZME0LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZME1LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZME8LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMX0DQ00JFAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/omx/RTM8RC0000ZMX0LQ00JPAQE_3_0_22.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/adsp/RTM8RC0000ZNA1SS00JFAQE_1_0_17.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/adsp/RTM8RC0000ZNA2DS00JFAQE_1_0_17.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/adsp/RTM8RC0000ZNA3SS00JFAQE_1_0_17.zip"
    required_file "vendor/renesas/$outer_zip_name/source/proprietary/adsp/RTM8RC0000ZNA4SS00JFAQE_1_0_17.zip"

    check_required_files_result
    failed_prereqs=

    cd "$PROJDIR/vendor/renesas/$outer_zip_name/source/bsp"
    pkg="$inner_zip_name.zip"
    echo "Unzipping inner package: $pkg"
    unzip -o "$pkg"

    section "Restructure files into pkgs_dir according to instructions"
    # Restructure according to the instructions of the Renesas documentation:
    cd $inner_zip_name || {
       echo failed to cd to $inner_zip_name
       exit 4
    }
    rm -rf pkgs_dir
    mkdir pkgs_dir
    mv -f $PROJDIR/vendor/renesas/$outer_zip_name/source/proprietary/{omx,adsp,gfx} pkgs_dir/

    echo "NOTE: For R-Car target, source code fetch (repo sync) will be done in build script instead"
    section "Results of pkgs_dir ($PWD/pkgs_dir)"
    ls pkgs_dir
    cd -

    ;;
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    ;;
  hikey960)
    section "Repo Sync ($AASIGDP_TARGET)"
    ../bin/repo sync
    ;;
  hikey970)
    section "Repo Sync ($AASIGDP_TARGET)"
    # According to https://github.com/96boards/documentation/wiki
    # We should install local manifest from github before repo sync
    git clone https://github.com/96boards-hikey/android-manifest.git -b hikey970_v1.0 .repo/local_manifests
    ../bin/repo sync
    ;;
  *)
    section "UNEXPECTED TARGET ERROR"  # We should never reach this
    ;;
esac

section "INIT script is done."
