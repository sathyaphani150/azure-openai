from pathlib import Path

from helpdesk.ingestion.pdf_extractor import extract_pdf

REQUIRED_CONTENT = {
    "vpn-troubleshooting.pdf": (
        "connection and authentication failures",
        "credentials rejected",
        "frequent disconnection",
    ),
    "wifi-troubleshooting.pdf": (
        "cannot connect to a listed network",
        "slow wi-fi",
        "wireless adapter",
    ),
    "password-reset.pdf": ("forgotten", "account lockout", "mfa"),
    "laptop-troubleshooting.pdf": (
        "power, startup, and boot problems",
        "overheating",
        "keyboard",
    ),
    "software-installation.pdf": (
        "before installation",
        "administrator permission",
        "safe uninstall and reinstall",
    ),
    "microsoft-365-troubleshooting.pdf": (
        "outlook mail",
        "teams meetings",
        "onedrive, sharepoint, word, and excel",
    ),
    "it-support-policy.pdf": (
        "supported scope",
        "support channels and hours",
        "information required when raising a ticket",
    ),
}


def test_all_required_pdfs_exist_and_cover_assignment_topics() -> None:
    """The generated controlled corpus retains each required document and core topics."""
    directory = Path("knowledge-base/pdf")
    assert {path.name for path in directory.glob("*.pdf")} == set(REQUIRED_CONTENT)
    for filename, expected_phrases in REQUIRED_CONTENT.items():
        pages = extract_pdf(directory / filename)
        assert len(pages) >= 4, f"{filename} should be a page-structured runbook"
        text = "\n".join(page.text for page in pages).lower()
        for phrase in expected_phrases:
            assert phrase in text, f"{filename} is missing assignment topic: {phrase}"
