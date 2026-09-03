import json
from pathlib import Path

from app.embeddings.cohere_embeddings import generate_embeddings

INPUT_FILE = Path("data/processed/chunks.json")
OUTPUT_FILE = Path("data/processed/embedded_chunks.json")

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file {INPUT_FILE} does not exist.")

    chunks = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("No chunks found in the input file.")

    texts = [chunk["text"] for chunk in chunks]

    print(f"Found {len(texts)} chunks.")
    print("Generating Cohere embeddings...")

    embeddings = generate_embeddings(texts)

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Number of embeddings does not match number of chunks."
        )

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    OUTPUT_FILE.write_text(
        json.dumps(
            chunks,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Successfully saved embeddings to: {OUTPUT_FILE}"
    )

    print(
        f"Embedding dimension: {len(embeddings[0])}"
    )


if __name__ == "__main__":
    main()