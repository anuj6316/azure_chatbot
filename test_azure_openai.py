#!/usr/bin/env python3
"""Test script to verify Azure OpenAI configuration and list deployments."""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Get configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip('/')
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
deployment_name = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-ada-002")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

print("=" * 60)
print("Azure OpenAI Configuration Test")
print("=" * 60)
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment_name}")
print(f"API Version: {api_version}")
print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
print()

if not endpoint or not api_key:
    print("❌ ERROR: Missing endpoint or API key!")
    print("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file")
    exit(1)

try:
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )
    
    print("✅ Successfully connected to Azure OpenAI")
    print()
    
    # Try to list deployments using Azure Management API
    print("Fetching deployments...")
    print("⚠️  Note: Cannot list deployments via OpenAI API directly.")
    print("   Use Azure Portal or Azure CLI to check deployments.")
    print()
    print("To check deployments via Azure CLI:")
    print(f"   az cognitiveservices account deployment list \\")
    print(f"     --resource-group <your-resource-group> \\")
    print(f"     --name openai6316")
    print()
    print("Or check in Azure Portal:")
    print(f"   1. Go to: https://portal.azure.com")
    print(f"   2. Navigate to: Azure OpenAI → openai6316")
    print(f"   3. Click: 'Model deployments' or 'Deployments'")
    print()
    
    # Test embeddings call
    print("\n" + "=" * 60)
    print("Testing Embeddings API...")
    print("=" * 60)
    
    try:
        response = client.embeddings.create(
            model=deployment_name,
            input="test"
        )
        print(f"✅ Embeddings API works!")
        print(f"   Vector dimension: {len(response.data[0].embedding)}")
    except Exception as e:
        print(f"❌ Embeddings API failed: {e}")
        if "DeploymentNotFound" in str(e):
            print(f"\n💡 The deployment '{deployment_name}' doesn't exist.")
            print("   Please check the deployment name in Azure Portal.")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify endpoint is correct (should be: https://your-resource.openai.azure.com)")
    print("2. Verify API key is correct")
    print("3. Check if Azure OpenAI resource exists and is accessible")

