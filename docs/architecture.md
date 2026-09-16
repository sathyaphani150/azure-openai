# Architecture

## Runtime components

The POC is a modular FastAPI application. HTTP routes validate input and invoke focused services. Services depend on an `AIProvider` protocol rather than importing Azure directly, making core behavior testable with a deterministic fake.

The Azure provider uses the OpenAI Python SDK's asynchronous Azure client. Authentication is selected at configuration time: API key or an Entra bearer-token provider backed by `DefaultAzureCredential`. Chat, embeddings, and vision use separately configured deployment names.

## Retrieval flow

Ingestion reads PDFs page by page, normalizes extracted text, creates overlapping token chunks, embeds batches, normalizes vectors, and writes vectors, chunk metadata, content fingerprints, and a versioned compatibility manifest. Fingerprints hash canonical extracted page text rather than raw PDF bytes, so regenerated metadata does not invalidate unchanged content. FAISS performs inner-product search over normalized vectors when installed; NumPy provides equivalent exact cosine search otherwise.

The controlled corpus is maintained as reviewable Markdown and generated as page-numbered PDFs. Content is structured around symptoms and decision points rather than generic advice. Every runbook includes rapid triage, safety boundaries, verification, escalation criteria, and evidence required for a useful support ticket.

At query time, the same provider/deployment embeds the question. A shared check used by startup, readiness, and retrieval rejects manifest-version, provider, deployment, chunk-setting, or PDF-content mismatches. The service retrieves top-k chunks above the configured threshold, constructs bounded context, and asks the chat deployment to answer only from that context. Results expose source, page, similarity score, and excerpt.

For a single-instance POC, optional startup ingestion loads a compatible persisted index or rebuilds it before requests are served. Azure App Service should place this index under persistent `/home`. Concurrent writers are intentionally out of scope; multi-worker or scaled deployments should use one controlled ingestion job or an external managed vector store.

## Trust boundaries

- Browser input, PDF text, and images are untrusted.
- Retrieved text cannot override the system prompt.
- Uploads are held in memory, size-limited, decoded, and never persisted.
- Configuration status exposes booleans and missing variable names, never values.
- Generated index files contain controlled document text and need filesystem protection.
- The local UI has no employee authentication and is intended for loopback demonstration.

## Failure modes

Azure exceptions map to a stable public error contract. No-result behavior bypasses chat generation and escalates safely. `/health` remains available when Azure or the index is unconfigured, while `/ready` returns 503 until configuration and the index are compatible.
