import json
import glob
import os
import re

INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/cleaned"

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = glob.glob(os.path.join(INPUT_DIR, "*.json"))

# Avoid processing the same DailyMed Set ID more than once.
seen_set_ids = set()

total_sections = 0
total_characters = 0

for file_path in sorted(files):
    filename = os.path.basename(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sections = json.load(file)

        if not isinstance(sections, list) or not sections:
            print(f"Skipped invalid file: {filename}")
            continue

        set_id = sections[0].get("set_id")

        if not set_id:
            print(f"Skipped file without Set ID: {filename}")
            continue

        if set_id in seen_set_ids:
            print(f"Skipped duplicate label: {filename}")
            continue

        seen_set_ids.add(set_id)

        # Extract the drug name from the label's XML title metadata
        # where available in the current extracted JSON.
        drug_name = sections[0].get("drug_name", "Unknown drug")

        # Replace introductory prescribing-information text with a
        # cleaner name inferred from the label's section headings.
        if drug_name.lower().startswith("these highlights do not include"):
            candidates = [
                section.get("section", "")
                for section in sections
                if section.get("section", "").strip()
            ]

            drug_name = candidates[0] if candidates else "Unknown drug"

        cleaned_sections = []

        for section in sections:
            text = section.get("text", "")

            # Normalize whitespace without changing the wording.
            text = re.sub(r"\s+", " ", text).strip()

            if not text:
                continue

            cleaned_section = {
                "drug_name": drug_name,
                "set_id": set_id,
                "version": section.get("version"),
                "effective_date": section.get("effective_date"),
                "section": section.get("section", "Untitled section"),
                "text": text,
                "source_url": section.get("source_url"),
            }

            cleaned_sections.append(cleaned_section)

        output_file = os.path.join(
            OUTPUT_DIR,
            f"{set_id}.json"
        )

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                cleaned_sections,
                file,
                indent=2,
                ensure_ascii=False,
            )

        characters = sum(len(item["text"]) for item in cleaned_sections)

        total_sections += len(cleaned_sections)
        total_characters += characters

        print(f"Cleaned: {drug_name}")
        print(f"  Sections: {len(cleaned_sections)}")
        print(f"  Characters: {characters:,}")

    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not process {filename}: {error}")

print("\n" + "=" * 55)
print("CORPUS CLEANING COMPLETE")
print("=" * 55)
print(f"Unique labels: {len(seen_set_ids)}")
print(f"Sections: {total_sections}")
print(f"Characters: {total_characters:,}")
print(f"Output directory: {OUTPUT_DIR}")