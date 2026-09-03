import re


def clean_markdown(text: str) -> str:
    """
    Clean extracted Markdown before chunking.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace from lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines at the beginning/end
    text = "\n".join(lines).strip()

    return text