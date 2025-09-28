#!/usr/bin/env bash
set -euo pipefail

STACK="${1:-dev}"
DOCKER_PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"
ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PULUMI_PROJECT="$(awk '/^name:/ {print $2; exit}' "$ROOT_DIR/infra/Pulumi.yaml")"
REGISTRY_NAME="$(echo "$PULUMI_PROJECT" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9')"
IMAGE="${REGISTRY_NAME}.azurecr.io/${PULUMI_PROJECT}:latest"
RESOURCE_GROUP="$PULUMI_PROJECT"
WEBAPP_NAME="${PULUMI_PROJECT}-app"

cd "$ROOT_DIR/infra"
if ! pulumi stack select "$STACK" >/dev/null 2>&1; then
  pulumi stack init "$STACK"
fi

echo "[deploy] Ensuring infrastructure exists via pulumi up on stack ${STACK}"
pulumi up --stack "$STACK" --yes

APP_URL=$(pulumi stack output --stack "$STACK" app_service_url)

cd "$ROOT_DIR"

echo "[deploy] Building Docker image ${IMAGE} for platform ${DOCKER_PLATFORM}"
docker build --platform "$DOCKER_PLATFORM" -t "$IMAGE" .

# Wait for the registry DNS to become available
MAX_ATTEMPTS=10
SLEEP_SECONDS=5
attempt=1
while [[ $attempt -le $MAX_ATTEMPTS ]]; do
  if az acr show --name "$REGISTRY_NAME" >/dev/null 2>&1; then
    break
  fi
  echo "[deploy] Waiting for ACR ${REGISTRY_NAME} to be ready... (${attempt}/${MAX_ATTEMPTS})"
  sleep $SLEEP_SECONDS
  attempt=$((attempt + 1))

done

if [[ $attempt -gt $MAX_ATTEMPTS ]]; then
  echo "[deploy] ACR ${REGISTRY_NAME} is not available after waiting. Exiting."
  exit 1
fi

echo "[deploy] Logging into Azure Container Registry ${REGISTRY_NAME}"
az acr login --name "$REGISTRY_NAME"

echo "[deploy] Pushing image ${IMAGE}"
docker push "$IMAGE"

echo "[deploy] Enabling container logging"
az webapp log config --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" --docker-container-logging filesystem >/dev/null

stream_logs() {
  echo "[deploy] Streaming container logs (30s timeout)"
  az webapp log tail --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" --timeout 30 | tee /tmp/webapp-log-tail.log

  if grep -iqE "(error|exception|fail)" /tmp/webapp-log-tail.log; then
    echo "[deploy] ⚠️ Detected potential errors in container logs"
  else
    echo "[deploy] ✅ No errors detected in the recent log tail"
  fi
}

echo "[deploy] Restarting web app ${WEBAPP_NAME}"
az webapp restart --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" || \
  echo "[deploy] Warning: could not restart web app (it may not exist yet)"

if [[ -n "$APP_URL" ]]; then
  echo "[deploy] App URL: https://$APP_URL"
else
  echo "[deploy] App URL not available. Use 'pulumi stack output app_service_url'."
fi

sleep 10
stream_logs || true

sleep 10
stream_logs || true

sleep 10
stream_logs || true
