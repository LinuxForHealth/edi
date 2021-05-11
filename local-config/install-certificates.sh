#!/usr/bin/env sh
# install-certificates.sh
# installs edi locally trusted Root CA and development certificates.

BASE_DIRECTORY=$(dirname "$0")

echo "install CA Root certificate"
mkcert -install
echo ""

echo "copy root ca to service directories"
CA_ROOT_LOCATION=$(mkcert -CAROOT)

for dir in app
do
  cp "$CA_ROOT_LOCATION"/rootCA.pem "$BASE_DIRECTORY"/"$dir"/lfh-root-ca.pem
done

echo "create edi development certificate"
echo ""
mkcert -cert-file "$BASE_DIRECTORY"/edi/edi-server.pem \
       -key-file "$BASE_DIRECTORY"/edi/edi-server.key \
       edi edi_edi_1 localhost 127.0.0.1 ::1
