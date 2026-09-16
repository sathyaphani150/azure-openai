# Azure OpenAI Advanced POC Assignment

## Objective

Create a complete technical guide for provisioning, configuring, authenticating, and consuming Azure OpenAI, and build an AI-powered IT Helpdesk Assistant demonstrating Azure setup, Playground experimentation, chat, embeddings, vision, prompt engineering, Python SDK usage, authentication, usage/quota awareness, pricing awareness, and error handling.

The POC must:

1. Accept IT-related questions.
2. Search a controlled IT knowledge base through semantic similarity.
3. Generate answers grounded in relevant knowledge-base content.
4. Analyze uploaded IT error screenshots.
5. Generate step-by-step troubleshooting guides from knowledge-base context.
6. Classify IT issues with zero-shot prompting.
7. Classify issues with few-shot prompting and compare the result with zero-shot.
8. Demonstrate System, User, and Assistant roles.
9. Demonstrate Azure OpenAI API-key authentication.
10. Demonstrate Microsoft Entra ID authentication.
11. Use the OpenAI Python SDK configured for Azure OpenAI.
12. Demonstrate usage, token consumption, pricing/quota awareness, and basic error handling.

## Required knowledge base

- `vpn-troubleshooting.pdf`: common issues, connection/authentication failures, disconnection, causes, steps, example errors, and escalation.
- `wifi-troubleshooting.pdf`: connection failure, frequent disconnection, no networks, slow Wi-Fi, adapter issues, and steps.
- `password-reset.pdf`: forgotten/expired passwords, reset, lockout, MFA, recovery, and escalation.
- `laptop-troubleshooting.pdf`: startup, performance, overheating, battery, display, keyboard/touchpad, and basic troubleshooting.
- `software-installation.pdf`: procedure, approved software, failures, permissions, updates, and reinstalling.
- `microsoft-365-troubleshooting.pdf`: Outlook, Teams, Word/Excel, sign-in, sync, and common steps.
- `it-support-policy.pdf`: supported applications, support hours, passwords, approved software, device policy, escalation, when to contact IT, and ticket information.

## Required RAG pipeline

PDFs -> extract text -> chunk documents -> generate embeddings -> store vectors -> embed user question -> similarity search -> top relevant chunks -> chat model -> grounded response.

Use an appropriate vector store such as FAISS, Chroma, or Azure AI Search and document the selection.

## Required error handling

- Invalid API key: user-friendly authentication error.
- Invalid or missing deployment: configuration error.
- HTTP 429: bounded retry or friendly retry response.
- Quota exhausted: friendly message with documented cause.
- No relevant result: state that information was not found and direct the employee to IT Support.
- Invalid or unsupported image: appropriate validation error.

## Required implementation and evidence

Provision or select the Azure resource and model deployments; test Chat, Completion, Embedding, and Image/vision capabilities in the Playground; prepare the PDFs; implement ingestion, embeddings, vector search, FastAPI, RAG, vision, guide generation, classification comparison, role prompts, both authentication modes, usage/error handling, a web UI, and end-to-end tests and documentation.

This file is a structured transcription of the supplied `.docx`; the `.docx` remains the primary source of truth.
