#!/usr/bin/env bash
# Publish the website from the NAS working copy to the folder nginx serves.
# Run on Alcyone:  bash /mnt/nas_projects/Projects/PersonalWebsite/deploy/publish.sh
set -euo pipefail

SRC="/mnt/nas_projects/Projects/PersonalWebsite"
DST="/home/nickkal/docker/personal-website"

mkdir -p "$DST/site" "$DST/nginx"

# Warn about uncommitted changes to the public files
if git -C "$SRC" status --porcelain -- index.html cv 2>/dev/null | grep -q .; then
  echo "WARNING: uncommitted changes in index.html or cv/ are being published."
fi

# Only the public files: index.html and the CV PDFs. Nothing else leaves the NAS.
rsync -a --delete --chmod=D755,F644 \
  --include='index.html' --include='cv/' --include='cv/*.pdf' --exclude='*' \
  "$SRC/" "$DST/site/"

# nginx config: copy and reload only when it changed
if ! cmp -s "$SRC/deploy/nginx.conf" "$DST/nginx/default.conf"; then
  install -m 644 "$SRC/deploy/nginx.conf" "$DST/nginx/default.conf"
  echo "nginx config updated."
  if docker ps --format '{{.Names}}' | grep -qx personal-website; then
    docker exec personal-website nginx -t && docker exec personal-website nginx -s reload && echo "nginx reloaded."
  fi
fi

echo "Published: $(git -C "$SRC" log -1 --format='%h %s' 2>/dev/null || echo 'unknown commit')"
find "$DST/site" -type f -printf '  %P  (%s bytes)\n' | sort
