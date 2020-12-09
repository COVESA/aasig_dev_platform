FROM ubuntu:18.04

RUN apt-get update

# Standard package list from https://source.android.com/setup/build/initializing#setting-up-a-linux-build-environment
RUN apt-get install -y git-core gnupg flex bison build-essential zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip fontconfig

# Renesas required additions, according to documentation
RUN apt-get install -y python-wand python-crypto liblz4-tool

# Other stuff I found missing in container base image, and/or convenience tools
RUN apt-get install -y rsync libncurses5-dev wget m4 bc

# Convenience tools for poking around inside container
RUN apt-get install -y vim-tiny

# With the latest version, repo seems to have included a python3 only statements
# and will completely fail (not only warn) on python2
# ... and later, the executable is expected to "python"
# ... and then this means the relevant python libraries (crypto) must be found
#     also in the python3 environment
# Workaround:
RUN apt-get install -y python3 python3-wand python3-crypto
RUN cd /usr/bin && rm python && ln -s python3 python

# The file rebuild_marker can be modified to force a (non-cache) rebuild
# but only from this point (e.g. avoiding the long apt-get commands)
# Place this where the rebuild should start from.
ADD rebuild_marker /tmp/dummy

RUN mkdir -p /aasig_dev_platform/bin
WORKDIR /aasig_dev_platform

# Necessary for repo later on , and it must be stored in --global apparently, so important to do it
# in container setup only, so we do not mess up the user's personal settings.
RUN git config --global user.name "AASIGDP Automated Build" ; git config --global user.email "no-email"

# Use files from local working dir instead (to ensure any local changes are
# also tested)
# NOTE! These files only exists after copying them from the working
# directory.  This will be done if the container is built using the
# Makefile.
ADD bin bin/
Add vendor vendor/

RUN ls -lR
RUN mkdir aosp
#RUN bin/init.sh
CMD bash
