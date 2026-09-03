import json
from pathlib import Path

from app.ingestion.cleaner import clean_markdown
from app.ingestion.chunker import create_chunks


INPUT_FILE = Path("data/processed/paper.md")
OUTPUT_FILE = Path("data/processed/chunks.json")


def main():

    markdown = INPUT_FILE.read_text(encoding="utf-8")

    # 1. Clean
    cleaned_markdown = clean_markdown(markdown)

    # 2. Chunk
    chunks = create_chunks(
        markdown=cleaned_markdown,
        doc_id="workhub-srs-001",
        title="WorkHub - Team Collaboration Platform",
    )

    # 3. Convert Pydantic objects to dictionaries
    data = [
        chunk.model_dump()
        for chunk in chunks
    ]

    # 4. Save JSON
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created {len(chunks)} chunks.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()