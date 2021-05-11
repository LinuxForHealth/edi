#!/usr/bin/env sh
# uninstall-certificates.sh
# removes the edi CA and other trusted certificates from the local trust store and file system
BASE_DIRECTORY=$(dirname "$0")

mkcert -uninstall

for dir in edi
do
  rm -f "$BASE_DIRECTORY"/"$dir"/*.pem
  rm -f "$BASE_DIRECTORY"/"$dir"/*.key
done
