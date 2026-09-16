from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from helpdesk.clients.factory import create_ai_provider
from helpdesk.config import get_settings
from helpdesk.ingestion.pipeline import ingest_knowledge_base


def build_pdfs(source_dir: Path, output_dir: Path) -> list[Path]:
    """Generate the controlled PDF corpus from its reviewable Markdown sources."""
    output_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    built: list[Path] = []
    for source in sorted(source_dir.glob("*.md")):
        output = output_dir / f"{source.stem}.pdf"
        document_title = source.stem.replace("-", " ").title()
        story = []
        for raw_line in source.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 0.12 * inch))
            elif line.startswith("# "):
                story.append(Paragraph(line[2:], styles["Title"]))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
            elif line.startswith("- "):
                story.append(Paragraph(f"- {line[2:]}", styles["BodyText"]))
            elif line == "---PAGE---":
                story.append(PageBreak())
            else:
                story.append(Paragraph(line, styles["BodyText"]))
        document = SimpleDocTemplate(
            str(output),
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        def draw_page_metadata(canvas, doc, title: str = document_title) -> None:
            """Add a document label and page number without exposing configuration."""
            canvas.saveState()
            canvas.setTitle(title)
            canvas.setAuthor("Azure OpenAI IT Helpdesk POC")
            canvas.setFont("Helvetica", 8)
            canvas.setFillGray(0.4)
            canvas.drawString(doc.leftMargin, 0.4 * inch, title)
            canvas.drawRightString(
                letter[0] - doc.rightMargin,
                0.4 * inch,
                f"Page {doc.page}",
            )
            canvas.restoreState()

        document.build(
            story,
            onFirstPage=draw_page_metadata,
            onLaterPages=draw_page_metadata,
        )
        built.append(output)
    return built


def build_pdfs_main() -> None:
    """Run the knowledge-base PDF generation command."""
    parser = argparse.ArgumentParser(description="Build the controlled IT knowledge-base PDFs.")
    parser.add_argument("--source", type=Path, default=Path("knowledge-base/source"))
    parser.add_argument("--output", type=Path, default=Path("knowledge-base/pdf"))
    args = parser.parse_args()
    built = build_pdfs(args.source, args.output)
    print(json.dumps({"built": [str(path) for path in built], "count": len(built)}, indent=2))


async def _ingest() -> None:
    settings = get_settings()
    provider = create_ai_provider(settings)
    try:
        report = await ingest_knowledge_base(settings, provider)
        print(json.dumps(asdict(report), indent=2))
    finally:
        await provider.close()


def ingest_main() -> None:
    """Run knowledge-base extraction, chunking, embedding, and persistence."""
    asyncio.run(_ingest())
