# Azure Portal Deployment

This procedure deploys the POC to Azure App Service without inventing resource, model, subscription, tenant, endpoint, deployment, or API-version values. Obtain every value from resources you own.

## 1. Prepare Azure OpenAI

1. In Microsoft Foundry or the Azure portal, select or create an approved Azure OpenAI resource in your chosen subscription and region.
2. Confirm quota and deploy models that support chat, embeddings, and image input. Record each **deployment name**; it can differ from the model name.
3. Record the resource endpoint and an API version supported by that resource and the OpenAI Python SDK.
4. Complete the Playground evidence described in `playground-validation.md` without recording credentials.

## 2. Create the web app

1. Create an Azure App Service **Web App** using a Linux Python runtime supported by this project (Python 3.11 or later).
2. For this local-vector-store POC, start with one App Service instance and one application process. Multiple concurrent startup writers are not supported.
3. Deploy the repository through Deployment Center, a ZIP deployment with build automation, or a container built from `Dockerfile`.
4. For source deployment, ensure `SCM_DO_BUILD_DURING_DEPLOYMENT=1`. The root `requirements.txt` installs the package and its dependencies.
5. For Python 3.13 or earlier, set **Configuration > General settings > Startup Command** to:

   ```text
   uvicorn helpdesk.main:app --host 0.0.0.0 --port 8000
   ```

The container image already supplies its startup command and runs as a non-root user.

## 3. Configure application settings

Under **Settings > Environment variables**, add the following names using values from your own resource:

| Setting | Value or source |
|---|---|
| `AI_PROVIDER` | `azure` |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_VERSION` | A supported API version you selected |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Your chat deployment name |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Your embedding deployment name |
| `AZURE_OPENAI_VISION_DEPLOYMENT` | Your vision-capable deployment name |
| `AZURE_OPENAI_AUTH_MODE` | Prefer `entra_id`; `api_key` is also implemented |
| `KNOWLEDGE_BASE_DIR` | `knowledge-base/pdf` |
| `VECTOR_STORE_DIR` | `/home/data/vector-store` |
| `KB_AUTO_INGEST` | `true` for this single-process POC |

Keep the default chunk settings unless you intentionally want a new index. Changing chunk settings or the embedding deployment causes automatic re-ingestion.

For a custom Linux container, also enable App Service storage before relying on `/home` persistence. For a built-in Linux Python runtime, runtime-created persistent files belong under `/home`.

## 4. Configure authentication

### Recommended: Microsoft Entra managed identity

1. Open the Web App's **Identity** page and enable its system-assigned identity.
2. On the Azure OpenAI resource, add a role assignment for that managed identity using **Cognitive Services OpenAI User** at the narrowest practical scope.
3. Set `AZURE_OPENAI_AUTH_MODE=entra_id` and do not set `AZURE_OPENAI_API_KEY`.

The application uses `DefaultAzureCredential`; App Service supplies the managed-identity token without a stored client secret. Role propagation can take several minutes.

### Alternative: API key

1. Set `AZURE_OPENAI_AUTH_MODE=api_key`.
2. Set `AZURE_OPENAI_API_KEY` using a secure App Service setting, preferably a Key Vault reference.
3. Never commit the key or a populated `.env` file.

These modes authenticate the backend to Azure OpenAI. They do not authenticate employees to the POC web UI; protect public access with App Service Authentication or network restrictions before non-demo use.

## 5. Health and first-start ingestion

1. Set App Service **Health Check** to `/health`.
2. Restart the web app and watch **Log stream**. The first start calls the configured embedding deployment and writes the versioned index to `/home/data/vector-store`.
3. Open `/health`; expect HTTP 200 and `status: ok`.
4. Open `/ready`; expect HTTP 200 and `status: ready` only after ingestion succeeds.
5. Open `/api/kb/status`; verify 7 documents, 31 chunks, `provider: azure`, and `compatible: true`.
6. Exercise questions, guides, screenshot analysis, both classifiers, and the role demonstration through the web UI.

If `/ready` returns 503, use its safe `missing_configuration`, `knowledge_base_reason`, or `startup_error` field with Log stream. Common causes are a missing setting, RBAC propagation, quota/throttling, an invalid deployment name, or a non-writable vector-store directory.

## 6. Operational boundaries

- Auto-ingestion consumes embedding quota only when the index is missing or incompatible.
- The application logs token usage when Azure returns it, but it does not fabricate monetary estimates. Check current pricing for the exact region, model, and deployment type.
- Keep one process while `KB_AUTO_INGEST=true`. Before scaling out, disable it and create the index once, or replace the local store with a managed shared vector service.
- Back up or recreate `/home/data/vector-store` from the version-controlled PDF corpus; the index is derived data.
- The Azure Developer CLI (`azd`) is optional for this Portal workflow and is not installed by this repository.

Official references: [Deploy Python/FastAPI to App Service](https://learn.microsoft.com/azure/app-service/quickstart-python), [configure Linux Python apps and persistent runtime files](https://learn.microsoft.com/azure/app-service/configure-language-python), and [Azure OpenAI with Microsoft Entra managed identity](https://learn.microsoft.com/azure/foundry-classic/openai/how-to/managed-identity).
