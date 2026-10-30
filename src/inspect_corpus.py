import json
import glob
import os

files = glob.glob("data/processed/*.json")

total_sections = 0
total_characters = 0

print("=" * 65)
print("PHARMAGUIDE RAG — CORPUS INSPECTION")
print("=" * 65)

for file_path in sorted(files):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sections = json.load(file)

        # Ignore files that do not contain a list of sections.
        if not isinstance(sections, list):
            print(f"\nSkipped unexpected format: {os.path.basename(file_path)}")
            continue

        valid_sections = [
            section for section in sections
            if isinstance(section, dict)
            and section.get("text", "").strip()
        ]

        characters = sum(
            len(section["text"])
            for section in valid_sections
        )

        total_sections += len(valid_sections)
        total_characters += characters

        print(f"\nFile: {os.path.basename(file_path)}")
        print(f"  Drug: {valid_sections[0].get('drug_name', 'Unknown') if valid_sections else 'Unknown'}")
        print(f"  Valid sections: {len(valid_sections)}")
        print(f"  Characters: {characters:,}")

        empty_count = len(sections) - len(valid_sections)
        if empty_count:
            print(f"  Empty/invalid sections: {empty_count}")

    except (OSError, json.JSONDecodeError) as error:
        print(f"\nCould not inspect {file_path}: {error}")

print("\n" + "=" * 65)
print(f"Total JSON files: {len(files)}")
print(f"Total valid sections: {total_sections}")
print(f"Total extracted characters: {total_characters:,}")
print("=" * 65)