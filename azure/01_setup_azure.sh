#!/usr/bin/env bash
# Day 3: Create all Azure resources from the terminal (Azure CLI).
# Prereq: install Azure CLI  ->  https://learn.microsoft.com/cli/azure/install-azure-cli
# Run:    az login   (browser opens)   then   bash azure/01_setup_azure.sh
set -euo pipefail

# ---- CHANGE THESE (storage account name must be globally unique, lowercase, 3-24 chars) ----
RG="rg-ecommerce-de"
LOCATION="centralindia"
STORAGE="ecomdl$RANDOM$RANDOM"       # e.g. ecomdl1234512345
ADF_NAME="adf-ecommerce-$RANDOM"
DBX_NAME="dbx-ecommerce"
# --------------------------------------------------------------------------------------------

echo "==> Resource group"
az group create --name "$RG" --location "$LOCATION" -o none

echo "==> Storage account (ADLS Gen2 = storage account with hierarchical namespace)"
az storage account create \
  --name "$STORAGE" --resource-group "$RG" --location "$LOCATION" \
  --sku Standard_LRS --kind StorageV2 --hns true -o none

KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)

echo "==> Containers: landing, bronze, silver, gold"
for c in landing bronze silver gold; do
  az storage fs create --name "$c" --account-name "$STORAGE" --account-key "$KEY" -o none
done

echo "==> Azure Data Factory"
az extension add --name datafactory --only-show-errors || true
az datafactory create --resource-group "$RG" --factory-name "$ADF_NAME" --location "$LOCATION" -o none

echo "==> Azure Databricks workspace"
az extension add --name databricks --only-show-errors || true
az databricks workspace create --resource-group "$RG" --name "$DBX_NAME" \
  --location "$LOCATION" --sku trial -o none || \
az databricks workspace create --resource-group "$RG" --name "$DBX_NAME" \
  --location "$LOCATION" --sku standard -o none

# Save names for the next scripts
cat > azure/.env <<EOF
RG=$RG
LOCATION=$LOCATION
STORAGE=$STORAGE
ADF_NAME=$ADF_NAME
DBX_NAME=$DBX_NAME
EOF

echo
echo "DONE. Values saved in azure/.env (do NOT commit this file)."
echo "Storage account : $STORAGE"
echo "ADF             : $ADF_NAME"
echo "Databricks      : $DBX_NAME"
