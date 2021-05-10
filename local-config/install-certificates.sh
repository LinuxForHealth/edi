#!/usr/bin/env sh
# install-certificates.sh
# installs {{ template }} locally trusted Root CA and development certificates.

BASE_DIRECTORY=$(dirname "$0")

echo "install CA Root certificate"
mkcert -install
echo ""

echo "copy root ca to service directories"
CA_ROOT_LOCATION=$(mkcert -CAROOT)

for dir in app
do
  cp "$CA_ROOT_LOCATION"/rootCA.pem "$BASE_DIRECTORY"/"$dir"/app-root-ca.pem
done

echo "create {{ template }} development certificate"
echo ""
mkcert -cert-file "$BASE_DIRECTORY"/app/app-server.pem \
       -key-file "$BASE_DIRECTORY"/app/app-server.key \
       app app_app_1 localhost 127.0.0.1 ::1
