# Build your image
docker build -t chatbot-app .

# Login to Azure (CLI needed for this step)
az login

# Create variables
ACR_NAME="chatbotacr6316"  # Must be globally unique
RESOURCE_GROUP="chatbot-rg"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create container registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get credentials and login
ACR_PASSWORD=$(az acr credential show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query "passwords[0].value" -o tsv)
docker login $ACR_NAME.azurecr.io --username $ACR_NAME --password $ACR_PASSWORD

# Tag and push image
docker tag chatbot-app $ACR_NAME.azurecr.io/chatbot-app:latest
docker push $ACR_NAME.azurecr.io/chatbot-app:latest
