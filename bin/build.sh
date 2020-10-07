#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"
MYDIR="$PWD"
PROJDIR="$MYDIR/.."

# Defaults
lunchconfig=hikey960-userdebug

# LOG helpers
section() {
  echo '========================================================================='
  echo "build.sh, Section: $1"
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
    ls -lR "$PROJDIR/vendor"
    exit 2
  else
    echo "Seems OK"
  fi
}

failed_prereqs=
# Set up any unique for initial repo init (or fail early if target not defined)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    section "Check prereq files again ($AASIGDP_TARGET)"
    required_file "vendor/nxp/imx-p9.0.0_2.3.0.tar.gz"
    lunchconfig=mek_8q-userdebug
    ;;
  # RENESAS R-Car M3 starter-kit
  h3ulcb)
    section "Set lunchconfig and env variables ($AASIGDP_TARGET)"
    # This was checked in init, but no harm checking again (fail early)
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
    section "Set lunchconfig ($AASIGDP_TARGET)"
    lunchconfig=TBD
    ;;
  hikey960)
    section "Set lunchconfig ($AASIGDP_TARGET)"
    lunchconfig=hikey960-userdebug
    ;;
  hikey970)
    section "Set lunchconfig ($AASIGDP_TARGET)"
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
failed_prereqs=
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    section "Unpacking vendor files ($AASIGDP_TARGET)"
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
    section "Re-check all prerequisite files ($AASIGDP_TARGET)"
    cd "$PROJDIR"
    # Sanity check prerequisites:

    # Inner package should be unzipped already:
    # pkg="RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"

    # For H3, a few checks of unpacked files...
    failed_prereqs=
    outer_zip_dir="vendor/renesas/REE-EG_Android-P-2019_08E-v3.21.0_H3"
    required_file "$outer_zip_dir/source/bsp/RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E.zip"

    # ... but those files should also already be copied to pkgs_dir by init script
    inner_zip_dir="$outer_zip_dir/source/bsp/RENESAS_RCH3M3M3N_Android_P_ReleaseNote_2019_08E"
    pkgs_dir="$inner_zip_dir/pkgs_dir"

    required_file "$pkgs_dir/gfx/RCH3G001A9001ZDO_1_1_0.zip"
    required_file "$pkgs_dir/gfx/RTM0RC7795GQGG0001SA90C_1_1_0.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XVVP8E30SA90C_3_0_19.zip"
    # For M3: RCM3G001A9001ZDO_1_1_0.zip
    # For M3: RTM0RC7796GQGG0001SA90C_1_1_0.zip
    # For M3N: RCN3G001A9001ZDO_1_1_0.zip
    # For M3N: RTM0RC7796GQGGB001SA90C_1_1_0.zip
    required_file "$pkgs_dir/adsp/RCG3AHFWN0203ZDP_1_0_16.zip"
    required_file "$pkgs_dir/adsp/RCG3AHIFA9001ZDP_1_0_16.zip"
    required_file "$pkgs_dir/adsp/RCG3AHPDA9001ZDO_1_0_16.zip"
    required_file "$pkgs_dir/adsp/RCG3AHPLN0203ZDO_1_0_16.zip"
    required_file "$pkgs_dir/omx/RCG3VUDRA9001ZDO_3_0_19.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XCMCTL30SA90C_3_0_19.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XV263D30SA90C_3_0_19.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XV264D30SA90C_3_0_19.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XV264E30SA90C_3_0_19.zip"
    required_file "$pkgs_dir/omx/RTM0AC0000XV265D30SA90C_3_0_19.zip"

    check_required_files_result
    failed_prereqs=

    cd "$inner_zip_dir"
    builddir="$inner_zip_dir/mydroid" # Will be created by walkthrough

    # RENESAS' buildenv script fails silently if mydroid already exists
    # (for example if we run the build twice) Let's fix that.
    sed -i 's/mkdir/mkdir -p/' ./buildenv.sh

    export PATH="$PATH:$PROJDIR/bin"  # to find repo
    ./walkthrough.sh H3
    ;;

  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    section "(EMPTY) Re-check all prerequisite files ($AASIGDP_TARGET)"
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  hikey960)
    section "(EMPTY) Re-check all prerequisite files ($AASIGDP_TARGET)"
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  hikey970)
    section "(EMPTY) Re-check all prerequisite files ($AASIGDP_TARGET)"
    echo
    echo "PLEASE IMPLEMENT $AASIGDP_TARGET in $0"
    ;;
  *)
    section "*** ERROR ***"
    echo
    echo UNEXPECTED VALUE for AASIGDP_TARGET # We should never reach this
    ;;
esac

check_required_files_result

# Set up and build
# Not using -x flag because it lists everything in the called
# scripts as well (envsetup, lunch, ... they are all scripts)
# Renesas unpack script
echo builddir is $builddir
cd "$builddir"
section "envsetup.sh"
echo '+ source ./build/envsetup.sh'
source ./build/envsetup.sh
set -x
section "lunch"
lunch "$lunchconfig" && make -j$((2*$(nproc)))
r=$?
set +x

# Additional modifications:
case $AASIGDP_TARGET in
   hikey960)
     section "Post-build modifications $(AASIGDP_TARGET) -- new kernel"
    # Replacing kernel with Android Generic Kernel Image (GKI), according to
    # instructions: https://source.android.com/setup/build/devices  

    set -x
    cd "$builddir"
    mkdir new_gki_kernel
    cd new_gki_kernel

    # Get source
    # ../../bin/repo init -u https://android.googlesource.com/kernel/manifest -b android12-5.4  # <- No longer available!
    ../../bin/repo init -u https://android.googlesource.com/kernel/manifest -b common-android-mainline

    ../../bin/repo sync -j8 -c

    # Compile
    rm -rf out
    BUILD_CONFIG=common/build.config.hikey960 build/build.sh

    # Copy (replace) results from kernel build into Android source tree
    cd ../device/linaro/hikey-kernel/hikey960/5.4 && rm -rf *
    cp "$builddir/new_gki_kernel/out/android12-5.4/dist/*" .

    # Concatenate dtb
    cd ../device/linaro/hikey-kernel/hikey960/5.4
    cat Image.gz hi3660-hikey960.dtb  >Image.gz-dtb

    # Rebuild userspace with this
    lunch hikey960-userdebug
    make TARGET_KERNEL_USE=5.4 HIKEY_USES_GKI=true -j$((2*$(nproc)))

    # Sanity check results
    required_file "$builddir/device/linaro/hikey-kernel/hikey960/5.4/hi3660-hikey960.dtb"
    required_file "$builddir/device/linaro/hikey-kernel/hikey960/5.4/Image.gz-dtb"
    # NOTE: There are alternative instructions to instea download a prebuilt generic kernel.  For example:
    #curl -L https://ci.android.com/builds/submitted/6814259/kernel_aarch64/latest/Image | gzip -c >Image.gz
    # ... and then concatenate the DTB onto it, etc.
    ;;
 
    hikey970) # Same?
    ;;

    # For all others, nothing more to do
    *)
    ;;
esac

section "Done.  Return code is $r"
echo ANDROID BUILD DONE
exit $r
