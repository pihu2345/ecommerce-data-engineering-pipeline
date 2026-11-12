#!/usr/bin/env bash
# Day 4: Deploy ADF linked service, datasets and pipeline from JSON (az CLI).
# Pipeline: copy CSVs  landing -> bronze (raw, as-is), then run Databricks notebooks.
set -euo pipefail
source azure/.env

KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)

TMP=$(mktemp -d)
sed -e "s|__STORAGE__|$STORAGE|g" -e "s|__ACCOUNT_KEY__|$KEY|g" \
  adf/linkedservice_adls.json > "$TMP/ls.json"

az datafactory linked-service create -g "$RG" --factory-name "$ADF_NAME" \
  --linked-service-name ls_adls --properties @"$TMP/ls.json" -o none
echo "linked service created"

az datafactory dataset create -g "$RG" --factory-name "$ADF_NAME" \
  --dataset-name ds_landing_csv --properties @adf/dataset_landing_csv.json -o none
az datafactory dataset create -g "$RG" --factory-name "$ADF_NAME" \
  --dataset-name ds_bronze_csv --properties @adf/dataset_bronze_csv.json -o none
echo "datasets created"

az datafactory pipeline create -g "$RG" --factory-name "$ADF_NAME" \
  --name pl_ingest_landing_to_bronze --pipeline @adf/pipeline_ingest.json -o none
echo "pipeline created: pl_ingest_landing_to_bronze"

echo
echo "Run it:"
echo "  az datafactory pipeline create-run -g $RG --factory-name $ADF_NAME --name pl_ingest_landing_to_bronze"
rm -rf "$TMP"
