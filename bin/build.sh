#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"
MYDIR="$PWD"

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

