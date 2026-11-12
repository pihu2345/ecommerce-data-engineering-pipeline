#!/usr/bin/env bash
# Day 3: Upload generated CSVs to the ADLS "landing" container.
#   Full load        -> landing/full/<table>/<table>.csv
#   Incremental load -> landing/incremental/<yyyy-mm-dd>/<table>.csv
set -euo pipefail
source azure/.env

KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)
MODE="${1:-full}"      # full | incremental

if [ "$MODE" = "full" ]; then
  for f in data/*.csv; do
    t=$(basename "$f" .csv)
    az storage fs file upload --file-system landing \
      --path "full/$t/$t.csv" --source "$f" \
      --account-name "$STORAGE" --account-key "$KEY" --overwrite -o none
    echo "uploaded $f -> landing/full/$t/$t.csv"
  done
else
  D=$(date +%F)
  for f in data/incremental/*.csv; do
    t=$(basename "$f" .csv)
    az storage fs file upload --file-system landing \
      --path "incremental/$D/$t.csv" --source "$f" \
      --account-name "$STORAGE" --account-key "$KEY" --overwrite -o none
    echo "uploaded $f -> landing/incremental/$D/$t.csv"
  done
fi
