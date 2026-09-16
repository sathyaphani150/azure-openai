# Azure OpenAI IT Helpdesk POC

A runnable FastAPI proof of concept for grounded IT support using Azure OpenAI chat, embeddings, and vision. It includes a controlled seven-document PDF knowledge base, semantic retrieval, RAG answers with sources, screenshot analysis, troubleshooting guides, classification comparisons, role demonstrations, two Azure authentication modes, usage logging, and a browser UI.

## What works without Azure

Health, configuration, the UI, PDF generation, and automated tests do not require Azure credentials. Set `AI_PROVIDER=fake` to ingest and exercise the complete flow with a deterministic local test provider. Fake mode is visibly identified and must not be represented as real AI analysis.

## Architecture

```text
Browser -> FastAPI -> services -> Azure OpenAI adapter
                         |-- chat deployment
                         |-- embedding deployment
                         `-- vision deployment

PDFs -> page extraction -> token chunks -> embeddings -> local vector store
Question -> query embedding -> cosine top-k -> grounded prompt -> cited answer
```

The local vector store uses FAISS when the optional native package is installed and a NumPy exact-search fallback otherwise. Both persist normalized vectors, chunk metadata, and an index compatibility manifest. See [docs/architecture.md](docs/architecture.md).

## Prerequisites

- Python 3.11 or later.
- For real AI calls: a user-owned Azure OpenAI or compatible Microsoft Foundry resource with chat, embedding, and vision-capable deployments.
- For Entra authentication: Azure CLI or another credential supported by `DefaultAzureCredential`, plus the required data-plane RBAC role.

This repository never supplies Azure resource names, endpoints, keys, subscription IDs, tenant IDs, API versions, deployment names, or model names.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,faiss]"
Copy-Item .env.example .env
```

If a FAISS wheel is unavailable, install `.[dev]`; the tested NumPy fallback will be used.

## Configuration

Copy `.env.example` to `.env` and fill values from your resource.

| Variable | Purpose |
|---|---|
| `AI_PROVIDER` | `azure` for Azure or `fake` for offline demonstration/tests |
| `AZURE_OPENAI_ENDPOINT` | Resource endpoint |
| `AZURE_OPENAI_API_VERSION` | API version supported by the selected resource |
| `AZURE_OPENAI_AUTH_MODE` | `api_key` or `entra_id` |
| `AZURE_OPENAI_API_KEY` | Required only in API-key mode |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Chat deployment name |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding deployment name |
| `AZURE_OPENAI_VISION_DEPLOYMENT` | Vision-capable deployment name |
| `KB_AUTO_INGEST` | Validate the index and rebuild it at process startup when needed |
| `KNOWLEDGE_BASE_DIR` | Source PDF directory (default `knowledge-base/pdf`) |
| `VECTOR_STORE_DIR` | Writable persisted index directory |

Deployment names can differ from model names. Never commit `.env`.

## Build and ingest the knowledge base

```powershell
helpdesk-build-pdfs
```

For a credential-free local run:

```powershell
$env:AI_PROVIDER = "fake"
helpdesk-ingest
```

For Azure, configure `.env`, leave `AI_PROVIDER=azure`, then run `helpdesk-ingest`. Re-ingest whenever PDF content, chunk settings, the embedding provider, or embedding deployment changes. PDF compatibility is based on normalized extracted text, so regenerating an unchanged PDF no longer causes a false stale-index error.

`KB_AUTO_INGEST=true` makes a single application process validate the index at startup and rebuild a missing, stale, or incompatible index before serving searches. Keep it `false` when multiple processes or instances share the same directory; perform one controlled ingestion instead.

The seven required PDF filenames are generated from reviewed Markdown runbooks. Each runbook contains symptom-based diagnosis, safe remediation, resolution checks, escalation triggers, and ticket evidence. The included support policy uses explicit placeholders for organization-specific contacts, hours, and SLAs and must be completed and approved before organizational use.

## Run

```powershell
uvicorn helpdesk.main:app --reload
```

Open `http://127.0.0.1:8000`; API documentation is at `/docs`.

Important endpoints:

- `GET /health`, `GET /ready`
- `GET /api/config/status`, `GET /api/kb/status`
- `POST /api/questions`
- `POST /api/screenshots/analyze`
- `POST /api/guides`
- `POST /api/classifications/compare`
- `POST /api/prompts/roles/demo`

`/health` is a liveness endpoint. `/ready` returns HTTP 200 only when Azure configuration and the index are compatible; otherwise it returns HTTP 503 with a safe reason.

## Deploy to Azure App Service

The repository supports either App Service source deployment (`requirements.txt`) or container deployment (`Dockerfile`). Do not deploy the local fake index: it is ignored by Git and excluded from the container. Configure Azure to create a real embedding index at startup.

For the simplest POC deployment, use Linux App Service with one process/instance, configure the startup command below, enable a system-assigned managed identity, set the required environment variables in App Service, and use `/health` for Health Check.

```text
uvicorn helpdesk.main:app --host 0.0.0.0 --port 8000
```

Use `VECTOR_STORE_DIR=/home/data/vector-store` and `KB_AUTO_INGEST=true` so the generated Azure index is persisted outside the deployed application directory. The exact Portal procedure and verification checklist are in [docs/azure-setup.md](docs/azure-setup.md).

## Authentication

For API-key mode, set `AZURE_OPENAI_AUTH_MODE=api_key` and the key environment variable. The key is never returned or logged. Use a managed secret store outside local development.

For Entra mode, set `AZURE_OPENAI_AUTH_MODE=entra_id` and omit the API key. The application uses `DefaultAzureCredential` and a renewable bearer-token provider for `https://cognitiveservices.azure.com/.default`. An administrator must grant the identity a suitable data-plane role, normally **Cognitive Services OpenAI User**, at the narrowest practical scope. Managed identity is preferred when hosted in Azure.

Optional service-principal values in `.env` are supported through `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET`. All three are required together. A lone `AZURE_CLIENT_ID` can select a user-assigned managed identity.

These modes authenticate the backend to Azure OpenAI; they do not add employee login to the UI. See [docs/authentication.md](docs/authentication.md).

## Grounding and security

- Retrieved PDF text is untrusted reference data, not executable instructions.
- Low-relevance questions are escalated instead of fabricated.
- The assistant never requests passwords, MFA codes, API keys, or recovery codes.
- Images are content-validated as PNG, JPEG, or WebP and are not persisted.
- Logs exclude prompts, documents, screenshots, credentials, and bearer tokens.
- The UI applies output escaping before rendering model text.
- Keep the unauthenticated POC bound to localhost.

## Usage, quota, pricing, and errors

AI operations emit request ID, feature, latency, and available token usage. No monetary estimate is fabricated; use current Azure pricing for the deployed model, region, and deployment type.

The adapter provides friendly errors for authentication, missing deployments, throttling/quota, network timeouts, empty responses, and malformed structured output. Transient 429/connection/timeout errors use bounded exponential backoff with jitter.

## Tests

```powershell
pytest
ruff check .
```

Automated tests use fake providers and do not call Azure. See [docs/azure-setup.md](docs/azure-setup.md), [docs/playground-validation.md](docs/playground-validation.md), and [docs/demo-script.md](docs/demo-script.md) for live validation and presentation.

The `tests/` folder is intentionally retained: it protects authentication, PDF content, retrieval quality, grounding, image validation, classification, usage accounting, and API behavior without consuming Azure quota.
