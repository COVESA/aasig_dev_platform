Containers for aasig_dev_platform/
===================================

This directory contains Dockerfiles and scripts to set up controlled
container environments for more repeatable tests of the init/update/build
scripts, etc.

Requirements:
-------------

A Make program, probably GNU Make, is required.
```
apt-get update
apt-get install -y make
```

Some convenience scripts do this for you in the normal case but for the docker
environment you will be required to define the variable $AASIGDP_TARGET before
make build.

Usage:
------

Prepare:
(The Makefile will assume you are standing in the same directory)
```
cd docker
```

Build:
```
make build
```

Run:
```
make run
```

List (as normal)
```
docker ps
```

Interact:
```
make shell
```
This drops you into bash inside the container. Once inside container, you may
want to trigger the bin/update.sh script to download sources.  Of course,
since AOSP is huge, consider the troubleshooting section.

Kill and remove
```
make kill
```

For more, look into Makefile.

Troubleshooting
---------------

1) The container name "/aasigdp" is already in use by container ...

You have already run "make run" before so there is a container with the same
name.  The reason the name is fixed is to allow other commands like "make
shell" to refer to the right container.  Solution: learn to manage existing
containers with the docker frontend, or you run "make kill" to get rid of it.
Then try "make run" again.


2) Other issues.

Since AOSP is huge, it is definitely possible that you run out of disk space
(possibly only the space available to the docker container images*)
*Reconfiguring docker is out of scope for this README.  Go and search for it.

