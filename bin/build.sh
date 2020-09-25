#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"
MYDIR="$PWD"

# Defaults
lunchconfig=hikey960-userdebug

# Helper functiosn
fail_target() {
  echo "Unknown target ($AASIGDP_TARGET).  Please make sure variable \$AASIGDP_TARGET is set to a known value."
  exit 1
}

required_file() {
  local d="$PWD"
  cd "$MYDIR/.."  # files specified relative to root of project
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

failed_prereqs=
# Set up any unique for initial repo init (or fail early if target not defined)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    required_file "vendor/nxp/imx-p9.0.0_2.3.0.tar.gz"
    lunchconfig=mek_8q-userdebug
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

# Continue with additional steps (Unpack, apply patches etc.)
failed_prereqs=
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
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    ;;
  hikey960)
    ;;
  hikey970)
    ;;
  *)
    echo UNEXPECTED  # We should never reach this
    ;;
esac

check_required_files_result

cd ../aosp

# Set up and build
# Not using -x flag because it lists everything in the called
# scripts as well (envesetup, lunch, ... they are all scripts)
cd "$MYDIR/../aosp"
echo '+ source ./build/envsetup.sh'
source ./build/envsetup.sh
set -x
lunch $lunchconfig
make -j$((2*$(nproc)))
set +x

# Additional modifications:
case $AASIGDP_TARGET in
   hikey960)
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

echo ANDROID BUILD DONE
