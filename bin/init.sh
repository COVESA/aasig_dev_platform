#!/bin/bash

# Start from bin dir
cd "$(dirname "$0")"

# Default
builddir="$PWD/../aosp"

# Defaults

#PROJDIR=/workdir
PROJDIR=$PWD/..

# According to https://source.android.com/setup/build/downloading
REPO_SHA=d06f33115aea44e583c8669375b35aad397176a411de3461897444d247b6c220

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

    ;;
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    manifest=TBD
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
   ../bin/repo init -u $url -b $branch $manifest $flags
else
   echo "Repo url is unset => no init at this time"
fi
set +x

# Update repo command from local copy to avoid nagging warnings
#(Note, on some platforms using SELinux, manipulating binaries
# like this might possibly fail)
echo "Copying locally initialized repo command to $(readlink -f ../bin/) to make sure it is up to date."
cp .repo/repo/repo ../bin/repo
chmod 755 ../bin/repo

# Continue with additional steps for init
cd "$builddir"  # (later changed for special targets like Renesas)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
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

