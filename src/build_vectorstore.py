import json
import os

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "data/processed/chunks.json"
DB_PATH = "chroma_db"
COLLECTION_NAME = "pharmaguide"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64


def main():
    print("Loading document chunks...")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        raise ValueError("No chunks found. Run the chunking script first.")

    print(f"Loaded {len(chunks)} chunks.")

    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("\nInitializing Chroma database...")
    client = chromadb.PersistentClient(path=DB_PATH)

    # Rebuild the collection to avoid retaining stale or duplicate chunks.
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("Removed the previous collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print("\nGenerating embeddings and storing chunks...")

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [item["text"] for item in batch]
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        ids = [item["chunk_id"] for item in batch]

        metadatas = [
            {
                "drug_name": item.get("drug_name") or "Unknown drug",
                "set_id": item.get("set_id") or "",
                "version": str(item.get("version") or ""),
                "effective_date": str(item.get("effective_date") or ""),
                "section": item.get("section") or "Unknown section",
                "source_url": item.get("source_url") or "",
            }
            for item in batch
        ]

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Stored {min(start + len(batch), len(chunks))}/{len(chunks)} chunks")

    print("\n" + "=" * 55)
    print("VECTOR DATABASE CREATED SUCCESSFULLY")
    print("=" * 55)
    print(f"Database directory: {os.path.abspath(DB_PATH)}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Stored chunks: {collection.count()}")
    print(f"Embedding model: {MODEL_NAME}")


if __name__ == "__main__":
    main()