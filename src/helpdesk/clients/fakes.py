from __future__ import annotations

import json
import math
import re

from helpdesk.clients.protocols import AITextResponse
from helpdesk.schemas import UsageInfo


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class FakeAIProvider:
    """Deterministic provider for local development and offline automated tests."""

    dimension = 256

    async def embed(self, texts: list[str]) -> tuple[list[list[float]], UsageInfo]:
        vectors: list[list[float]] = []
        prompt_tokens = 0
        concepts = (
            ("vpn", "tunnel", "remote access"),
            ("wifi", "wi-fi", "wireless", "network adapter"),
            ("password", "mfa", "account lock", "credentials", "sign-in"),
            ("laptop", "battery", "overheat", "keyboard", "touchpad", "screen"),
            ("software", "install", "uninstall", "application update", "permissions"),
            ("outlook", "teams", "word", "excel", "microsoft 365", "onedrive"),
            (
                "support hours",
                "business hours",
                "raise a ticket",
                "support ticket",
                "ticket information",
                "device support",
                "approved software",
            ),
        )
        for text in texts:
            vector = [0.0] * self.dimension
            words = _tokens(text)
            prompt_tokens += len(words)
            lowered = text.lower()
            for index, keywords in enumerate(concepts):
                vector[index] = float(sum(lowered.count(keyword) for keyword in keywords))
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors, UsageInfo(prompt_tokens=prompt_tokens, total_tokens=prompt_tokens)

    async def chat(
        self,
        messages: list[dict[str, object]],
        *,
        deployment: str | None = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        response_format: dict[str, str] | None = None,
    ) -> AITextResponse:
        del deployment, max_tokens, temperature
        prompt = "\n".join(str(message.get("content", "")) for message in messages)
        lower = prompt.lower()
        if response_format:
            issue = str(messages[-1].get("content", "")).lower()
            category = self._category(issue)
            payload = {
                "category": category,
                "confidence": 0.9 if category != "Other" else 0.55,
                "rationale": f"The issue contains signals associated with {category}.",
            }
            text = json.dumps(payload)
        elif "troubleshooting guide" in lower:
            text = (
                "## Troubleshooting guide\n\n"
                "1. Record the exact error and when it occurred.\n"
                "2. Follow the relevant knowledge-base checks shown in the cited sources.\n"
                "3. Retry the operation and verify whether service is restored.\n"
                "4. If the issue remains, contact IT Support with the error, device, and steps tried."
            )
        elif "knowledge-base context" in lower:
            final_user_message = str(messages[-1].get("content", ""))
            context = final_user_message.split("KNOWLEDGE-BASE CONTEXT", 1)[-1]
            excerpt = re.sub(r"\s+", " ", context).strip()[:500]
            text = "Offline grounded demo. Relevant retrieved context: " + excerpt
        else:
            text = (
                "This offline demonstration shows how system, user, and assistant roles are sent."
            )
        usage = UsageInfo(
            prompt_tokens=len(_tokens(prompt)),
            completion_tokens=len(_tokens(text)),
            total_tokens=len(_tokens(prompt)) + len(_tokens(text)),
        )
        return AITextResponse(text=text, usage=usage)

    async def analyze_image(
        self, prompt: str, image_data_url: str, *, max_tokens: int = 900
    ) -> AITextResponse:
        del image_data_url, max_tokens
        text = (
            "Offline vision demo: the image passed validation. Configure Azure OpenAI to receive "
            "a real screenshot diagnosis. Capture the exact error text, application, and recent changes."
        )
        return AITextResponse(
            text=text,
            usage=UsageInfo(
                prompt_tokens=len(_tokens(prompt)),
                completion_tokens=len(_tokens(text)),
                total_tokens=len(_tokens(prompt)) + len(_tokens(text)),
            ),
        )

    @staticmethod
    def _category(text: str) -> str:
        rules = [
            ("VPN", ("vpn", "tunnel", "remote access")),
            ("Wi-Fi", ("wifi", "wi-fi", "wireless", "network")),
            ("Password", ("password", "locked", "mfa", "sign in")),
            ("Laptop", ("laptop", "battery", "overheat", "keyboard", "screen")),
            ("Microsoft 365", ("outlook", "teams", "word", "excel", "microsoft 365")),
            ("Software", ("install", "uninstall", "software", "application")),
        ]
        for category, keywords in rules:
            if any(keyword in text for keyword in keywords):
                return category
        return "Other"

    async def close(self) -> None:
        return None
