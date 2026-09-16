from __future__ import annotations

from uuid import uuid4

from helpdesk.clients.protocols import AIProvider
from helpdesk.observability.usage import elapsed_timer, log_usage
from helpdesk.schemas import RoleDemoResponse, RoleMessage


class RoleDemoService:
    """Demonstrate System, User, and Assistant roles in one model call."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def demonstrate(self, question: str, request_id: str | None = None) -> RoleDemoResponse:
        """Return the inspectable role messages and resulting assistant response."""
        request_id = request_id or str(uuid4())
        messages = [
            RoleMessage(
                role="system",
                content="You are a concise IT assistant. Never ask for passwords or MFA codes.",
            ),
            RoleMessage(
                role="user", content="My VPN connection failed after I changed my password."
            ),
            RoleMessage(
                role="assistant",
                content=(
                    "Reconnect using the new password. If cached credentials remain, remove the saved "
                    "VPN credential without sharing it, then retry."
                ),
            ),
            RoleMessage(role="user", content=question),
        ]
        with elapsed_timer() as elapsed:
            response = await self.provider.chat([message.model_dump() for message in messages])
            log_usage(
                feature="role_demo",
                request_id=request_id,
                usage=response.usage,
                latency_ms=elapsed(),
            )
        return RoleDemoResponse(
            messages=messages,
            response=response.text,
            usage=response.usage,
            request_id=request_id,
        )
