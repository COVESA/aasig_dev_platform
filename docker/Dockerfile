FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y build-essential zlibc git curl python-wand python-crypto gnupg vim-tiny libncurses5-dev \
                       unzip liblz4-tool wget m4 ccache flex bison zip bc

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
