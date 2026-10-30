import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "chroma_db"
COLLECTION_NAME = "pharmaguide"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    print(f"Database contains {collection.count()} chunks.")

    question = input("\nEnter your question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )

    print("\n" + "=" * 65)
    print("RETRIEVAL RESULTS")
    print("=" * 65)

    for index, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        print(f"\nResult {index}")
        print(f"Drug: {metadata.get('drug_name')}")
        print(f"Section: {metadata.get('section')}")
        print(f"Set ID: {metadata.get('set_id')}")
        print(f"Cosine distance: {distance:.4f}")
        print(f"Source: {metadata.get('source_url')}")
        print(f"\nText:\n{document[:1200]}")
        print("-" * 65)


if __name__ == "__main__":
    main()