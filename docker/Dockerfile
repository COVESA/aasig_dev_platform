FROM ubuntu:19.04

ARG AASIGDP_TARGET=hikey970

RUN apt-get update
RUN apt-get install -y build-essential zlibc git curl python gnupg vim-tiny

# The file rebuild_marker can be modified to force a (non-cache) rebuild
# but only from this point (e.g. avoiding the long apt-get commands)
# Place this where the rebuild should start from.
ADD rebuild_marker /tmp/dummy

RUN mkdir -p /aasig_dev_platform/bin
WORKDIR /aasig_dev_platform

# Use files from local working dir instead (to ensure any local changes are
# also tested)
# NOTE! These files only exists after copying them from the working
# directory.  This will be done if the container is built using the
# Makefile.
ADD init*.sh bin/
ADD update*.sh bin/

RUN mkdir aosp
RUN bin/init.sh
CMD bash
