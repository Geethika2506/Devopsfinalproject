#!/usr/bin/env bash
set -e

RG="sddo-rg"
LOCATION="westeurope"
ACR_NAME="sddoacr$RANDOM"    # change as you like (must be globally unique)
PLAN_NAME="sddo-plan"
WEBAPP_NAME="sddo-webapp-$RANDOM"  # change as you like (must be unique)
INSIGHTS_NAME="sddo-ai"

echo "Creating resource group..."
az group create -n $RG -l $LOCATION

echo "Creating ACR..."
az acr create -n $ACR_NAME -g $RG --sku Basic

echo "Creating App Service plan (Linux, reserved) ..."
az appservice plan create -g $RG -n $PLAN_NAME --is-linux --sku B1

echo "Creating Web App for Containers..."
az webapp create -g $RG -p $PLAN_NAME -n $WEBAPP_NAME --deployment-container-image-name hello-world

echo "Create Application Insights (optional)..."
az monitor app-insights component create -g $RG -a $INSIGHTS_NAME -l $LOCATION --application-type web

echo "Resource creation complete."
echo "ACR: $ACR_NAME"
echo "WebApp: $WEBAPP_NAME"
echo "AppInsights: $INSIGHTS_NAME"
