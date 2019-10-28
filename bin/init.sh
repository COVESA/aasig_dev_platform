#!/bin/sh

# Start from bin dir
cd "$(dirname "$0")"

# Defaults
url=https://android.googlesource.com/platform/manifest
branch=master
manifest=""

# According to https://source.android.com/setup/build/downloading
REPO_SHA=d06f33115aea44e583c8669375b35aad397176a411de3461897444d247b6c220

# Helper functiosn
fail_target() {
    echo "Unknown target ($AASIGDP_TARGET).  Please make sure variable \$AASIGDP_TARGET is set to a known value."
    exit 1
}

# Set up any unique for initial repo init (or fail early if target not defined)
case $AASIGDP_TARGET in
  # NXP i.mx8 (e.g. EVK board)
  imx8)
    manifest="-m imx-p9.0.0_2.3.0.xml"
    url=https://source.codeaurora.org/external/imx/imx-manifest.git
    branch=imx-android-pie
    ;;
  # RENESAS R-Car M3 starter-kit
  m3ulcb)
    manifest=TBD
    ;;
  hikey960)
    ;;
  hikey970)
    echo UNTESTED
    manifest=""
    ;;
  *)
    fail_target
    ;;
esac

curl https://storage.googleapis.com/git-repo-downloads/repo > ./repo
chmod a+x ./repo

sha256sum </dev/null >/dev/null || echo "Could not run sha256sum??"

if [ "$(sha256sum ./repo | cut -c 1-64)" != "$REPO_SHA" ] ; then
  echo "Hash mismatch -> repo version was updated?  Check it before running..."
  echo "Expected: $REPO_HASH"
  echo -n "Got: " ; sha256sum repo
  echo "You might check https://source.android.com/setup/build/downloading for update"
fi

echo "For git configuration, please provide name and email."
echo "(This will ONLY be stored in project-local git config variables:"
echo "user.name and user.email)"
read -p "Full name : " name
read -p "Email: " email
git config --global user.name "$name"
git config --global user.email "$email"
cd ../aosp


set -x
../bin/repo init -u $url -b $branch $manifest
set +x

# Update repo command from local copy to avoid nagging warnings
#(Note, on some platforms using SELinux, manipulating binaries
# like this might possibly fail)
echo "Copying locally initialized repo command to $(readlink -f ../bin/) to make sure it is up to date."
cp .repo/repo/repo ../bin/repo
chmod 755 ../bin/repo

# Continue with additional steps for init
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
    git clone https://github.com/96boards-hikey/android-manifest.git -b hikey970_v1.0 .repo/local_manifests
    ;;
  *)
    echo UNEXPECTED  # We should never reach this
    ;;
esac

