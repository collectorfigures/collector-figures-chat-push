#!/bin/sh
set -eu

cd "$(dirname "$0")"

if [ ! -f service_account.json ]; then
  tmp_key="$(mktemp)"
  trap 'rm -f "$tmp_key"' EXIT
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$tmp_key" >/dev/null 2>&1
  python3 - "$tmp_key" <<'PY'
import json
import pathlib
import sys

private_key = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
fixture = {
    "type": "service_account",
    "project_id": "mock-project-id-12345",
    "private_key_id": "runtime-generated-test-fixture",
    "private_key": private_key,
    "client_email": "mock-service-account@mock-project-id-12345.iam.gserviceaccount.com",
    "client_id": "123456789012345678901",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mock-service-account%40mock-project-id-12345.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}
pathlib.Path("service_account.json").write_text(
    json.dumps(fixture, indent=2) + "\n",
    encoding="utf-8",
)
PY
  chmod 0600 service_account.json
fi

if [ ! -d out ]; then
  mkdir out
  chmod ugo+rwX out
fi

if [ ! -d mitmproxy ]; then
  mkdir mitmproxy
  chmod ugo+rwX mitmproxy
fi

if [ ! -f mitmproxy/mitmproxy-ca.pem ]; then
  openssl genrsa --out mitmproxy/ca.key 4096
  # Generate a mitmproxy CA
  # According to instructions from https://docs.mitmproxy.org/stable/concepts/certificates/
  openssl req -x509 -new -nodes -key mitmproxy/ca.key -sha256 -out mitmproxy/ca.crt -addext keyUsage=critical,keyCertSign -subj '/CN=MyOrg Root CA/C=GB/ST=MySt/L=MyL/O=MyOrg'
  cat mitmproxy/ca.key mitmproxy/ca.crt > mitmproxy/mitmproxy-ca.pem
  chmod ugo+rwX mitmproxy/ca.crt mitmproxy/ca.key mitmproxy/mitmproxy-ca.pem
fi

