#!/bin/sh
if [ $# -ne 1 ]
then
  echo ***ERROR: Missing KVStore Install Directory 
  echo Usage: $0 \<KVStore Root Install Dir\>
  exit 1
fi
IMAGE=ppoddar/kvlite
KVHOME=$1
if [ -d $KVHOME/lib ]
then
 echo Building Docker Image $IMAGE from KVStore $KVHOME
 mkdir tmp
 cp $KVHOME/lib/* tmp/
 docker build -q -t $IMAGE .
 rm -rf tmp
else
 echo ***ERROR: KVStore libraries $KVHOME/lib do not exist.
 exit 2
fi 
