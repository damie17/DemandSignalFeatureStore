#!/bin/bash
# =============================================================
# Azure Setup Script for Demand Signal Feature Store
# Creates: Resource Group, Key Vault, Azure OpenAI + Model Deployment
# =============================================================

# 1. Define Environment Variables
RESOURCE_GROUP="rg-ai-services-prod"
LOCATION="eastus"
KEYVAULT_NAME="kv-aiservice-prod-$RANDOM"
SECRET_NAME="ApiKeySecret"
IDENTITY_NAME="id-aiservice-user"
OPENAI_NAME="openai-demandstore-$RANDOM"     # Azure OpenAI resource name (globally unique)
OPENAI_DEPLOYMENT="gpt-4o"                    # Deployment name we'll use in our code
OPENAI_MODEL="gpt-4o"                        # Model to deploy (change to gpt-4o-mini or gpt-35-turbo if needed)

echo "============================================="
echo "Resource Group:  $RESOURCE_GROUP"
echo "Location:        $LOCATION"
echo "Key Vault:       $KEYVAULT_NAME"
echo "OpenAI Resource: $OPENAI_NAME"
echo "Model:           $OPENAI_MODEL"
echo "============================================="

# ----- Step 1: Create the Resource Group -----
echo ""
echo ">>> Step 1: Creating Resource Group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# ----- Step 2: Create Azure OpenAI Resource -----
echo ""
echo ">>> Step 2: Creating Azure OpenAI resource..."
az cognitiveservices account create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0 \
  --custom-domain $OPENAI_NAME

# ----- Step 3: Deploy a Model -----
echo ""
echo ">>> Step 3: Deploying model ($OPENAI_MODEL)..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name $OPENAI_DEPLOYMENT \
  --model-name $OPENAI_MODEL \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

# ----- Step 4: Retrieve OpenAI Key and Endpoint -----
echo ""
echo ">>> Step 4: Retrieving OpenAI credentials..."
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

echo ""
echo "============================================="
echo "YOUR AZURE OPENAI CREDENTIALS"
echo "============================================="
echo "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT"
echo "AZURE_OPENAI_API_KEY=$OPENAI_KEY"
echo "AZURE_OPENAI_DEPLOYMENT=$OPENAI_DEPLOYMENT"
echo "============================================="
echo "SAVE THESE VALUES — you will need them for your .env file"
echo "============================================="

# ----- Step 5: Create the Key Vault -----
echo ""
echo ">>> Step 5: Creating Key Vault..."
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization true

# ----- Step 6: Assign Key Vault Roles -----
echo ""
echo ">>> Step 6: Assigning Key Vault roles..."
USER_ID=$(az ad signed-in-user show --query id -o tsv)
KV_ID=$(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)

az role assignment create \
  --assignee $USER_ID \
  --role "Key Vault Secrets Officer" \
  --scope $KV_ID

echo "Waiting 15s for RBAC propagation..."
sleep 15

# ----- Step 7: Store OpenAI Key in Key Vault -----
echo ""
echo ">>> Step 7: Storing OpenAI key in Key Vault..."
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "AzureOpenAIKey" \
  --value "$OPENAI_KEY"

az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "AzureOpenAIEndpoint" \
  --value "$OPENAI_ENDPOINT"

# ----- Step 8: Additional Role Assignments (Optional) -----
echo ""
echo ">>> Step 8: Additional role assignments..."

az role assignment create \
  --assignee $USER_ID \
  --role "Key Vault Administrator" \
  --scope $KV_ID

az role assignment create \
  --assignee $USER_ID \
  --role "Contributor" \
  --scope $KV_ID

# ----- Step 9: Verify Everything -----
echo ""
echo ">>> Step 9: Verifying setup..."
echo ""
echo "--- OpenAI Resource ---"
az cognitiveservices account show \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Endpoint:properties.endpoint, Kind:kind, SKU:sku.name}" \
  -o table

echo ""
echo "--- Model Deployment ---"
az cognitiveservices account deployment list \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Model:properties.model.name, Version:properties.model.version}" \
  -o table

echo ""
echo "--- Key Vault Secrets ---"
az keyvault secret list \
  --vault-name $KEYVAULT_NAME \
  --query "[].name" \
  -o table

echo ""
echo "--- Role Assignments ---"
az role assignment list \
  --scope $KV_ID \
  --query "[].{Principal:principalName, Role:roleDefinitionName}" \
  -o table

echo ""
echo "============================================="
echo "SETUP COMPLETE"
echo "============================================="
echo ""
echo "For your .env file, use:"
echo ""
echo "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT"
echo "AZURE_OPENAI_API_KEY=$OPENAI_KEY"
echo "AZURE_OPENAI_DEPLOYMENT=$OPENAI_DEPLOYMENT"
echo "AZURE_OPENAI_API_VERSION=2024-12-01-preview"
echo ""
echo "============================================="
