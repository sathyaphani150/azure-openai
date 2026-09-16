# Azure OpenAI IT Helpdesk POC

## Project Goal

Build the complete Azure OpenAI End-to-End POC described in:
docs/assignment.md

The goal is to implement the assignment as a working, testable
Python application, not merely produce example code.

## Source of Truth

The assignment document is the primary source of truth for:
- Required functionality
- Knowledge-base requirements
- Architecture
- Authentication requirements
- Prompt engineering requirements
- Error handling requirements
- Expected POC capabilities

Do not silently remove or simplify a required assignment feature.

If a technical implementation detail is not specified by the assignment,
choose a sensible POC implementation and document the decision.

## Implementation Principles

- Use Python.
- Use FastAPI for the backend.
- Use the OpenAI Python SDK configured for Azure OpenAI.
- Keep Azure credentials out of source code.
- Use environment variables / .env for local development.
- Implement the knowledge-base ingestion pipeline.
- Implement document chunking.
- Implement Azure OpenAI embeddings.
- Implement vector similarity search.
- Implement RAG.
- Implement vision/screenshot analysis.
- Implement troubleshooting-guide generation.
- Implement zero-shot classification.
- Implement few-shot classification.
- Demonstrate System/User/Assistant roles.
- Implement API-key authentication.
- Implement Microsoft Entra ID authentication.
- Implement token/usage logging.
- Implement basic quota/rate-limit/error handling.
- Implement a simple web UI.
- Include tests for important application components.

## Development Approach

Work incrementally.

Before implementing a major feature:
1. Inspect the existing repository.
2. Read the relevant assignment requirements.
3. Explain the implementation plan briefly.
4. Implement the feature.
5. Run relevant tests/checks.
6. Fix errors.
7. Update documentation where necessary.

Do not create unnecessary infrastructure.

This is a POC, so prefer simple, maintainable implementations
over production-scale complexity.

## Important

Do not invent Azure configuration values.

Azure endpoint URLs, API keys, deployment names, model names,
subscription information, and Entra ID configuration must come
from environment variables or user-provided configuration.

Do not require Azure credentials to be committed to the repository.

## Definition of Done

The project is complete only when:
- The application can run locally.
- The knowledge base can be ingested.
- Embeddings can be generated.
- Vector similarity search works.
- RAG responses work.
- Screenshot analysis works when configured.
- Guide generation works.
- Zero-shot and few-shot classification work.
- Both authentication approaches are implemented/documented.
- Errors are handled gracefully.
- Usage/token information is captured where available.
- The web UI can exercise the major POC features.
- Tests/checks have been run.
- README/documentation explains setup and execution.