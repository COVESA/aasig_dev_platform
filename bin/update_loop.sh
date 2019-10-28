#!/bin/sh -xe

cd "$(dirname $0)/../aosp"
while true ; do 
../bin/repo sync && exit
sleep 200
done

