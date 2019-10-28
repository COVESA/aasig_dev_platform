#!/bin/sh -xe

cd "$(dirname "$0")/../aosp"

../bin/repo sync
if [ $? -ne 0 ] ; then
  echo
  echo "NOTE! Sometimes repo sync fails!"
  echo
  echo "You might need to simply retry the command "repo sync" inside of the $PWD directory until all sources have been downloaded."
fi

