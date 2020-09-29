#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"
MYDIR="$PWD"
PROJDIR="$MYDIR/.."

# Defaults
lunchconfig=hikey960-userdebug

failed_prereqs=

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
    required_file "vendor/nxp/imx-p9.0.0_2.3.0.tar.gz"
    lunchconfig=mek_8q-userdebug
    ;;
  # RENESAS R-Car M3 starter-kit
  h3ulcb)
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3.zip"
    lunchconfig=kingfisher-userdebug

    # For the later build steps:
    export TARGET_BOARD_PLATFORM=r8a7795  # H3
    export H3_OPTION=8GB
    export BUILD_BOOTLOADERS=true
    export BUILD_BOOTLOADERS_SREC=true
    ;;

  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    lunchconfig=TBD
    ;;
  hikey960)
    lunchconfig=hikey960-userdebug
    ;;
  hikey970)
    echo UNTESTED
    lunchconfig=hikey970-userdebug
    ;;
  *)
    fail_target
    ;;
esac

check_required_files_result

# (Default, could be modified)
builddir="$PROJDIR/aosp"

# Continue with additional steps (Unpack, apply patches etc.)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    cd ../aosp
    pkg="../vendor/nxp/imx-p9.0.0_2.3.0.tar.gz"
    echo "Unpacking $pkg"
    # We need to strip off the unnecessary top level dir named "imx-p9.0.0_2.3.0/"
    # This unpacks into aosp directory, and consequently aosp/vendor/nxp/...
    tar --strip-components=1 -xf $pkg  
    cd -
    ;;
  # RENESAS R-Car H3 starter-kit
  h3ulcb)

    pkg="../vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3.zip"
    pkg="REE-EG_Android-P-2019_08E-v3.21.0_H3.zip"
    echo "Unpacking $pkg"
    cd "$PROJDIR/vendor/renesas"
    unzip -u $pkg

    # Sanity check results:

    # For H3:
    failed_prereqs=
    required_file "vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/bsp/RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"
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
    #rm -rf RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E
    unzip -ou "RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"

    # Restructure according to the instructions of the Renesas documentation:
    cd RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E || {
       echo failed to cd to RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E
       exit 4
    }
    mkdir -p pkgs_dir
    mv -f $PROJDIR/vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3/source/proprietary/{omx,adsp,gfx} pkgs_dir/
    ls pkgs_dir

    # Renesas unpack script
echo CWD is 
pwd

    export workdir="$PWD"
    builddir="$workdir/mydroid"
    
    # RENESAS buildenv script fails silently if mydroid already exists
    # (for example if we end up running the build twice)
    # Let's fix that.
    sed -i 's/mkdir/mkdir -p/' ./buildenv.sh

    export PATH="$PATH:$PROJDIR/bin"  # to find repo
    ./walkthrough.sh H3
    cd -

    ;;

  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  hikey960)
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  hikey970)
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  *)
    echo
    echo UNEXPECTED VALUE for AASIGDP_TARGET # We should never reach this
    ;;
esac

check_required_files_result

# Set up and build
# Not using -x flag because it lists everything in the called
# scripts as well (envesetup, lunch, ... they are all scripts)
# Renesas unpack script
echo builddir is $builddir
cd "$builddir"
echo '+ source ./build/envsetup.sh'
source ./build/envsetup.sh
set -x
#lunch "$lunchconfig" && make -j$((2*$(nproc)))
lunch "$lunchconfig" && make -j8
r=$?
set +x
exit $r
