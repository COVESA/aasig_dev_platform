#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"

# Defaults
lunchconfig=hikey960-userdebug

# Helper functiosn
fail_target() {
    echo "Unknown target ($AASIGDP_TARGET).  Please make sure variable \$AASIGDP_TARGET is set to a known value."
    exit 1
}

# Set up any unique for initial repo init (or fail early if target not defined)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    lunchconfig=evk_8mm-userdebug
    ;;
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    lunchconfig=TBD
    ;;
  hikey960)
    ;;
  hikey970)
    echo UNTESTED
    lunchconfig=hikey970-userdebug
    ;;
  *)
    fail_target
    ;;
esac


# Continue with additional steps (apply patches etc.)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
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

