#!/bin/bash
# Monitor Azure App Service deployment progress

APP_NAME="oc-student-project-7-app"
RG="oc-student-project-7"
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo "=== Deployment Monitor for $APP_NAME ==="
echo ""

# 1. Current container config
echo "📦 Container Image:"
az webapp config container show --name $APP_NAME --resource-group $RG --query "[?name=='DOCKER_CUSTOM_IMAGE_NAME'].value" -o tsv 2>/dev/null

echo ""
echo "🕐 Last Modified:"
az webapp show --name $APP_NAME --resource-group $RG --query "lastModifiedTimeUtc" -o tsv 2>/dev/null

echo ""
echo "📊 App State:"
az webapp show --name $APP_NAME --resource-group $RG --query "state" -o tsv 2>/dev/null

echo ""
echo "🔄 Checking app health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$APP_URL")
echo "HTTP Status: $HTTP_CODE"

echo ""
echo "📜 Recent container logs (last 30 lines):"
echo "-------------------------------------------"
az webapp log tail --name $APP_NAME --resource-group $RG --timeout 5 2>/dev/null | head -30 || echo "(timeout - app may still be starting)"

echo ""
echo "-------------------------------------------"
echo "💡 Tip: If stuck, try restarting the app:"
echo "   az webapp restart --name $APP_NAME --resource-group $RG"
