# Deploying Your RAG Chatbot to Azure Container Apps

This guide provides step-by-step instructions to deploy your entire containerized application (frontend, backend, and Qdrant database) to Azure Container Apps, with persistent storage for your vector data.

We will use a shell script (`deploy.sh`) to automate the creation of all necessary Azure resources.

## Azure Services Used

*   **Azure Resource Group:** A container to hold all related resources for your application.
*   **Azure Container Registry (ACR):** A private registry to store and manage your custom Docker images.
*   **Azure Storage Account & File Share:** To provide a persistent file share for Qdrant's data, ensuring your vectors are not lost when the container restarts.
*   **Azure Container Apps Environment:** A secure, isolated boundary for running your container apps.
*   **Azure Container Apps:** The serverless platform that will run your three containers.

## Prerequisites

1.  **Azure CLI:** You must have the Azure CLI installed. You can find installation instructions [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
2.  **Logged in to Azure:** Open a terminal and run `az login` to authenticate with your Azure account.
3.  **Docker:** The Docker daemon must be running on your local machine to build and push the images.

## Deployment Steps

### 1. Configure the Deployment Script

I will create a `deploy.sh` script for you. Before running it, you will need to open this file and customize the variables at the top to match your preferences (e.g., for resource names and location). All resources will be created with these names.

### 2. Run the Deployment Script

Once you have configured the variables, make the script executable and run it from your terminal:

```bash
chmod +x deploy.sh
./deploy.sh
```

The script will perform the following actions:
*   Create the Azure resources (Resource Group, ACR, Storage Account, File Share).
*   Build your `rag_chatbot` and `frontend` Docker images.
*   Tag the images and push them to your new Azure Container Registry.
*   Deploy your entire application using the `docker-compose.yml` file to Azure Container Apps. This includes setting up the persistent storage for Qdrant.

The deployment may take several minutes to complete.

### 3. Access Your Application

Once the script finishes, it will print the public URL for your frontend application. You can open this URL in your browser to access your chatbot.

### 4. Cleaning Up

When you no longer need the application, you can delete all the created resources by deleting the resource group. This will prevent you from incurring further costs.

The `deploy.sh` script will contain a commented-out command to do this. You can uncomment it and run the script again, or run the command manually:

```bash
# Be careful! This will delete all the resources created.
# az group delete --name YOUR_RESOURCE_GROUP_NAME --yes
```
