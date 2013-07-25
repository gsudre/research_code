#!/bin/sh
# Script to clean up the stupid @eaDir folders created by AFP and SMB mounts
find /volume1/neuro/ -name "@eaDir" -type d -print |while read FILENAME; do rm -rf "${FILENAME}"; done

