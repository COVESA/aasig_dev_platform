#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"

# Default
builddir="$PWD/../aosp"

# Defaults

#PROJDIR=/workdir
PROJDIR=$PWD/..

#PROJDIR=/workdir
PROJDIR=$PWD/..

# According to https://source.android.com/setup/build/downloading
REPO_SHA=d73f3885d717c1dc89eba0563433cec787486a0089b9b04b4e8c56e7c07c7610

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
    manifest="-m imx-p9.0.0_2.3.0.xml"
    url=https://source.codeaurora.org/external/imx/imx-manifest.git
    branch=imx-android-pie
    flags=
    ;;

  # RENESAS R-Car H3 starter-kit
  h3ulcb)
    # This is all controlled by the provided RENESAS scripts
    manifest=
    url=
    branch=
    flags=
    export builddir=INVALID  # Not used here
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3.zip"
    # Link the unique build results path for convenience
    rm -f build_result  # (if exists)
    ln -s "$PROJDIR/vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/bsp/RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E/mydroid/out/target/product/kingfisher" "$PROJDIR/build_result"
    ;;

  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    manifest=TBD
    export TARGET_BOARD_PLATFORM=r8a7796
    # (M3N: TARGET_BOARD_PLATFORM=r8a77965)
    ;;

  hikey960)
    # According to: https://source.android.com/setup/build/devices (Checked 2020-09)
    url=https://android.googlesource.com/platform/manifest
    branch=master
    manifest=""  # (use default)
    flags=
    ;;

  hikey970)
    echo UNTESTED
    # According to https://github.com/96boards/documentation/wiki
    url=https://android.googlesource.com/platform/manifest
    branch=android-9.0.0_r8
    flags="--no-repo-verify --repo-branch=stable"
    ;;

  *)
    fail_target
    ;;
esac

check_required_files_result
failed_prereqs=

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

set -x
cd "$builddir"

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
set +x

# Continue with additional steps for init
cd "$builddir"  # (later changed for special targets like Renesas)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    ;;
  # RENESAS R-Car H3 starter-kit
  h3ulcb)
    cd $PROJDIR/vendor/renesas
    pkg="REE-EG_Android-P-2019_08E-v3.21.0_H3.zip"
    echo "Unpacking $pkg"
    unzip -u "$pkg"

    # Sanity check results:

    failed_prereqs=
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/bsp/RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"
    check_required_files_result

    # For H3:
    failed_prereqs=
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/gfx/RCH3G001A9001ZDO_1_1_0.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/gfx/RTM0RC7795GQGG0001SA90C_1_1_0.zip"
    # For M3: RCM3G001A9001ZDO_1_1_0.zip
    # For M3: RTM0RC7796GQGG0001SA90C_1_1_0.zip
    # For M3N: RCN3G001A9001ZDO_1_1_0.zip
    # For M3N: RTM0RC7796GQGGB001SA90C_1_1_0.zip

    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/adsp/RCG3AHFWN0203ZDP_1_0_16.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/adsp/RCG3AHIFA9001ZDP_1_0_16.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/adsp/RCG3AHPDA9001ZDO_1_0_16.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/adsp/RCG3AHPLN0203ZDO_1_0_16.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RCG3VUDRA9001ZDO_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XCMCTL30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XV263D30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XV264D30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XV264E30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XV265D30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVCMND30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVCMNE30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVM4VD30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVVP8D30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVVP8E30SA90C_3_0_19.zip"
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/omx/RTM0AC0000XVVP9D30SA90C_3_0_19.zip"

    check_required_files_result
    failed_prereqs=

    cd "$PROJDIR/vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/bsp"
    pkg="RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"
    echo "Unzipping inner package: $pkg"
    unzip -u "$pkg"

    # Restructure according to the instructions of the Renesas documentation:
    cd RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E/
    rm -rf pkgs_dir
    mkdir pkgs_dir
set -x
    mv $PROJDIR/vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/{omx,adsp,gfx} pkgs_dir/

    ls pkgs_dir
    echo "RENESAS: Additional unpacking will be done in build script"
    cd -

    ;;
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    ;;
  hikey960)
    ../bin/repo sync
    ;;
  hikey970)
    # According to https://github.com/96boards/documentation/wiki
    # We should install local manifest from github before repo sync
    git clone https://github.com/96boards-hikey/android-manifest.git -b hikey970_v1.0 .repo/local_manifests
    ../bin/repo sync
    ;;
  *)
    echo UNEXPECTED  # We should never reach this
    ;;
esac

