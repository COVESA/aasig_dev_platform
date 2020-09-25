FROM ubuntu:18.04

ARG AASIGDP_TARGET=hikey970

RUN apt-get update
RUN apt-get install -y build-essential zlibc git curl python3 gnupg vim-tiny libncurses5-dev unzip

# Make sure /usr/bin/python actually means python3
RUN cd /usr/bin && rm -f python && ln -s python3 python

# The file rebuild_marker can be modified to force a (non-cache) rebuild
# but only from this point (e.g. avoiding the long apt-get commands)
# Place this where the rebuild should start from.
ADD rebuild_marker /tmp/dummy

RUN mkdir -p /aasig_dev_platform/bin
WORKDIR /aasig_dev_platform

# To avoid issues with repo later on, we must define some name/email
RUN git config --global user.name "AASIG DP Dockefile"
RUN git config --global user.email "No-email"

# Use files from local working dir instead (to ensure any local changes are
# also tested)
# NOTE! These files only exists after copying them from the working
# directory.  This will be done if the container is built using the
# Makefile.
ADD bin/*.sh bin/

# To avoid issues with repo later on
RUN git config --global user.name "AASIG DP Dockefile"
RUN git config --global user.email "No-email"

RUN ls -lR
RUN mkdir aosp
RUN bin/init.sh
CMD bash
