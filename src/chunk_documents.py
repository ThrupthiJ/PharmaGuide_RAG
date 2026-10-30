import json
import glob
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

INPUT_DIR = "data/cleaned"
OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)

all_chunks = []
chunk_id = 0

for file_path in sorted(glob.glob(os.path.join(INPUT_DIR, "*.json"))):
    with open(file_path, "r", encoding="utf-8") as file:
        sections = json.load(file)

    for section in sections:
        text = section.get("text", "").strip()

        if not text:
            continue

        text_chunks = splitter.split_text(text)

        for text_chunk in text_chunks:
            all_chunks.append({
                "chunk_id": f"chunk_{chunk_id:05d}",
                "drug_name": section.get("drug_name", "Unknown drug"),
                "set_id": section.get("set_id"),
                "version": section.get("version"),
                "effective_date": section.get("effective_date"),
                "section": section.get("section", "Unknown section"),
                "text": text_chunk,
                "source_url": section.get("source_url"),
            })

            chunk_id += 1

output_file = os.path.join(OUTPUT_DIR, "chunks.json")

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_chunks, file, indent=2, ensure_ascii=False)

print("=" * 55)
print("DOCUMENT CHUNKING COMPLETE")
print("=" * 55)
print(f"Source labels: {len(glob.glob(os.path.join(INPUT_DIR, '*.json')))}")
print(f"Total chunks: {len(all_chunks)}")
print(f"Chunk size: 1000 characters")
print(f"Chunk overlap: 150 characters")
print(f"Output file: {output_file}")

if all_chunks:
    print("\nExample chunk:")
    print(json.dumps(all_chunks[0], indent=2, ensure_ascii=False))