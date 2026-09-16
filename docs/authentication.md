# Azure OpenAI Authentication

## API key

Set `AZURE_OPENAI_AUTH_MODE=api_key` and provide the endpoint, API version, key, and deployment names through environment variables. `.env` is ignored. Production hosting should use a managed secret store.

## Microsoft Entra ID

Set `AZURE_OPENAI_AUTH_MODE=entra_id`. The SDK receives a renewable token provider created from `DefaultAzureCredential` with the Azure Cognitive Services scope. Locally, the chain can use Azure CLI; Azure-hosted workloads should use managed identity.

When all three `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` values are supplied, the application uses `ClientSecretCredential`. Supplying only `AZURE_CLIENT_ID` selects a user-assigned managed identity through `DefaultAzureCredential`. Prefer managed identity over a client secret for hosted workloads.

An administrator must grant the identity a suitable Azure OpenAI data-plane role, typically `Cognitive Services OpenAI User`, at the narrowest workable scope. No subscription, tenant, resource-group, or resource values are included in this project.

Authentication support can vary across endpoint generations and resource types. Validate chat and embeddings with the exact endpoint/API version selected for the POC.

These modes authenticate the application to Azure OpenAI. They do not authenticate employees to FastAPI.
