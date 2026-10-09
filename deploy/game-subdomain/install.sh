#!/usr/bin/env bash
#
# Point game.gigumbrajaguru.me at the game page.
#
#   https://game.gigumbrajaguru.me/  →  301  →  https://gigumbrajaguru.me/game/
#
# The site itself is on GitHub Pages, which serves only one custom domain per repo
# (gigumbrajaguru.me), so the subdomain is answered by nginx on the myseer droplet
# and redirected. Query strings are kept, so campaign links (?utm_source=...) still
# reach analytics.
#
# Run from your machine:
#   ssh myseer 'sudo bash -s' < deploy/game-subdomain/install.sh
#
# Safe to re-run. nginx is only reloaded after `nginx -t` passes; on failure the
# previous config is restored, so the other sites on the box are never affected.
#
# TLS, in order of preference:
#   1. CERT=/path/fullchain.pem KEY=/path/privkey.pem  (e.g. a Cloudflare origin cert)
#   2. An existing or new Let's Encrypt cert (works when the DNS record is not proxied)
#   3. A self-signed cert (works behind Cloudflare with SSL mode "Full", not "Full (strict)")

set -euo pipefail

DOMAIN=game.gigumbrajaguru.me
TARGET=https://gigumbrajaguru.me/game/
SITE=/etc/nginx/sites-available/$DOMAIN
LINK=/etc/nginx/sites-enabled/$DOMAIN
WEBROOT=/var/www/letsencrypt
SNIPPET=/etc/nginx/snippets/tls-baseline.conf
SELF_DIR=/etc/ssl/$DOMAIN

[[ $EUID -eq 0 ]] || { echo "Run as root (sudo)." >&2; exit 1; }
command -v nginx >/dev/null || { echo "nginx is not installed." >&2; exit 1; }
mkdir -p "$WEBROOT" /etc/nginx/sites-available /etc/nginx/sites-enabled

backup=""
[[ -f $SITE ]] && { backup=$(mktemp); cp "$SITE" "$backup"; }

restore() {
  if [[ -n $backup ]]; then cp "$backup" "$SITE"; else rm -f "$SITE" "$LINK"; fi
  echo "nginx -t failed; previous config restored, nothing reloaded." >&2
  exit 1
}

http_block() {
  cat <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ { root $WEBROOT; }
    location / { return 301 $TARGET\$is_args\$args; }
}
EOF
}

https_block() {
  local include=""
  [[ -f $SNIPPET ]] && include="    include $SNIPPET;"
  cat <<EOF

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name $DOMAIN;

    ssl_certificate     $1;
    ssl_certificate_key $2;
$include

    return 301 $TARGET\$is_args\$args;
}
EOF
}

apply() {
  ln -sf "$SITE" "$LINK"
  nginx -t || restore
  systemctl reload nginx
}

# Step 1: HTTP redirect, which also serves the Let's Encrypt challenge.
http_block > "$SITE"
apply

# Step 2: pick a certificate.
cert="${CERT:-}" key="${KEY:-}"
le=/etc/letsencrypt/live/$DOMAIN
if [[ -z $cert && -f $le/fullchain.pem ]]; then
  cert=$le/fullchain.pem key=$le/privkey.pem
fi
if [[ -z $cert ]] && command -v certbot >/dev/null; then
  if certbot certonly --webroot -w "$WEBROOT" -d "$DOMAIN" --non-interactive --agree-tos \
       --register-unsafely-without-email --keep-until-expiring; then
    cert=$le/fullchain.pem key=$le/privkey.pem
  else
    echo "Let's Encrypt failed (DNS not pointing here yet, or proxied by Cloudflare)." >&2
  fi
fi
if [[ -z $cert ]]; then
  mkdir -p "$SELF_DIR"
  if [[ ! -f $SELF_DIR/cert.pem ]]; then
    openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -subj "/CN=$DOMAIN" \
      -keyout "$SELF_DIR/key.pem" -out "$SELF_DIR/cert.pem" 2>/dev/null
    chmod 600 "$SELF_DIR/key.pem"
  fi
  cert=$SELF_DIR/cert.pem key=$SELF_DIR/key.pem
  echo "Using a self-signed cert: fine behind Cloudflare 'Full', not for direct visitors." >&2
fi

# Step 3: add HTTPS.
{ http_block; https_block "$cert" "$key"; } > "$SITE"
apply
[[ -n $backup ]] && rm -f "$backup"

echo "Installed. Check:"
curl -s --noproxy "*" -o /dev/null -w "  http  -> %{http_code} %{redirect_url}\n" -H "Host: $DOMAIN" http://127.0.0.1/ || true
curl -sk --noproxy "*" -o /dev/null -w "  https -> %{http_code} %{redirect_url}\n" --resolve "$DOMAIN:443:127.0.0.1" "https://$DOMAIN/" || true
