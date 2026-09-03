import re
import uuid

from app.ingestion.schemas import DocumentChunk, ChunkMetadata


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")


def split_into_sections(markdown: str):
    """
    Split Markdown into sections based on headings.
    """

    lines = markdown.splitlines()

    sections = []

    current_heading = None
    current_content = []

    for line in lines:

        match = HEADING_PATTERN.match(line)

        if match:
            # Save previous section
            if current_heading is not None:
                sections.append(
                    {
                        "heading": current_heading,
                        "text": "\n".join(current_content).strip(),
                    }
                )

            current_heading = match.group(2).strip()
            current_content = []

        else:
            current_content.append(line)

    # Save final section
    if current_heading is not None:
        sections.append(
            {
                "heading": current_heading,
                "text": "\n".join(current_content).strip(),
            }
        )

    return sections


def create_chunks(
    markdown: str,
    doc_id: str,
    title: str,
    max_characters: int = 2000,
):
    """
    Convert Markdown sections into metadata-aware chunks.
    """

    sections = split_into_sections(markdown)

    chunks = []

    for section in sections:

        section_name = section["heading"]
        section_text = section["text"]

        if not section_text:
            continue

        # If section is small enough, keep it as one chunk
        if len(section_text) <= max_characters:

            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    text=section_text,
                    metadata=ChunkMetadata(
                        doc_id=doc_id,
                        title=title,
                        section=section_name,
                    ),
                )
            )

        else:

            # Split large sections
            start = 0

            while start < len(section_text):

                end = start + max_characters

                chunk_text = section_text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=str(uuid.uuid4()),
                            text=chunk_text,
                            metadata=ChunkMetadata(
                                doc_id=doc_id,
                                title=title,
                                section=section_name,
                            ),
                        )
                    )

                start = end

    return chunks