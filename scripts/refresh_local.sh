#!/usr/bin/env bash
set -euo pipefail

PROJECT=/workspace/gas
RUNTIME=/workspace/.runtime/zasfe-gas-opinet-refresh
LOCK="$RUNTIME/run.lock"
mkdir -p "$RUNTIME"

exec 9>"$LOCK"
flock -n 9 || { printf '%s\n' 'zasfe-gas-opinet-daily-refresh: already running'; exit 0; }

cd "$PROJECT"
: "${OPINET_API_KEY:?OPINET_API_KEY is not available}"
git pull --rebase origin main
uv run --with pyproj python -m scripts.generate_data \
  --region 0203 \
  --fuel-product B027 \
  --anchor-name '롯데슈퍼프레시 신곡점' \
  --anchor-address '경기 의정부시 동일로 583'
python scripts/validate_data.py public/data.json

git add public/data.json
if git diff --cached --quiet; then
  printf '%s\n' 'zasfe-gas-opinet-daily-refresh: no data change'
else
  git commit -m 'chore: refresh local Opinet snapshot'
  git push origin main
  printf '%s\n' 'zasfe-gas-opinet-daily-refresh: snapshot pushed'
fi
