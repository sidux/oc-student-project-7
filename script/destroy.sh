#!/usr/bin/env bash
set -euo pipefail

STACK="${1:-dev}"
ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PULUMI_PROJECT="$(awk '/^name:/ {print $2; exit}' "$ROOT_DIR/infra/Pulumi.yaml")"
REGISTRY_NAME="$(echo "$PULUMI_PROJECT" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9')"
RESOURCE_GROUP="$PULUMI_PROJECT"
REPOSITORY="$PULUMI_PROJECT"
IMAGE_TAG="latest"
SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
SMART_DETECTION_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/microsoft.insights/actiongroups/Application Insights Smart Detection"

cleanup_smart_detection() {
  if az resource show --ids "$SMART_DETECTION_ID" >/dev/null 2>&1; then
    echo "[destroy] Deleting Application Insights Smart Detection action group"
    az resource delete --ids "$SMART_DETECTION_ID"
  else
    echo "[destroy] Smart Detection action group not found, skipping"
  fi
}

cd "$ROOT_DIR"
cleanup_smart_detection

cd "$ROOT_DIR/infra"
if pulumi stack select "$STACK" >/dev/null 2>&1; then
  echo "[destroy] Running pulumi destroy on stack ${STACK}"
  pulumi destroy --stack "$STACK" --yes
  pulumi stack rm "$STACK" --yes || true
else
  echo "[destroy] Pulumi stack ${STACK} not found, skipping"
fi

cd "$ROOT_DIR"
IMAGE="${REGISTRY_NAME}.azurecr.io/${REPOSITORY}:${IMAGE_TAG}"
echo "[destroy] Attempting to delete image ${IMAGE}"
if az acr repository show --name "$REGISTRY_NAME" --repository "$REPOSITORY" >/dev/null 2>&1; then
  az acr repository delete --name "$REGISTRY_NAME" --image "$REPOSITORY:${IMAGE_TAG}" --yes
else
  echo "[destroy] Repository ${REPOSITORY} not found in ${REGISTRY_NAME}, skipping image delete"
fi
