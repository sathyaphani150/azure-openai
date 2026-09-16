from __future__ import annotations

CATEGORIES = ("VPN", "Wi-Fi", "Password", "Laptop", "Software", "Microsoft 365", "Other")

CLASSIFIER_SYSTEM_PROMPT = """Classify one IT support issue.
Allowed categories: VPN, Wi-Fi, Password, Laptop, Software, Microsoft 365, Other.
Return a JSON object with exactly: category, confidence, rationale.
confidence must be a number from 0 to 1. Use Other when evidence is insufficient."""

FEW_SHOT_MESSAGES: list[dict[str, object]] = [
    {"role": "user", "content": "The remote access tunnel disconnects every few minutes."},
    {
        "role": "assistant",
        "content": '{"category":"VPN","confidence":0.98,"rationale":"Remote access tunnel failures are VPN issues."}',
    },
    {"role": "user", "content": "Outlook keeps asking me to sign in and will not sync mail."},
    {
        "role": "assistant",
        "content": '{"category":"Microsoft 365","confidence":0.97,"rationale":"Outlook authentication and sync are Microsoft 365 issues."}',
    },
    {"role": "user", "content": "My computer battery drains quickly and the fan is very hot."},
    {
        "role": "assistant",
        "content": '{"category":"Laptop","confidence":0.96,"rationale":"Battery and overheating symptoms concern laptop hardware."}',
    },
]
