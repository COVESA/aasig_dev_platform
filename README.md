AASIG Development Platform
==========================

An Android "Development Platform": This repository is just a common setup
to build AOSP for the targets currently used in development in the Android
for Automotive special interest group.  The scripts and configurations define
a shared working environment for future work on components and for testing
out ideas.  The repository gives a common view of targets, the used branches
and versions, as well as dependencies such as specific BSPs, where applicable.
This provides repeatability and also convenience and a quick starting point.

Branches:
---------

* **master**   - General, published, and mostly stable branch
* **develop**  - Miscellaneous WIP before it is sent to master.  Warning: This branch is likely to be rebased and force-pushed at any time
* **\<target\>** - Hardware/target specific branches might be used later on


Hardware:
---------

The planned supported platforms are best seen on [this Wiki page](https://at.projects.genivi.org/wiki/display/DIRO/Android+development+platform).
The scripts and directory structure should give the rest of the details of
what is actually implemented.
