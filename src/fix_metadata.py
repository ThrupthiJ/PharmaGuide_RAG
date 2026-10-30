import json
import glob
import os

INPUT_DIR = "data/cleaned"

# Verified ingredient/product names associated with our selected labels.
DRUG_NAMES = {
    "056072d8-6228-4914-831d-ee7c0661b742":
        "Metformin Hydrochloride",
    "0daf1be9-ea38-461e-e063-6394a90a7954":
        "Ibuprofen (Ibuwin Forte)",
    "10e766cc-c3fd-4584-a0d7-652c516e828c":
        "Atorvastatin Calcium",
    "113e66f1-b922-8533-e063-6294a90ab30e":
        "Cetirizine Hydrochloride",
    "36efc48d-f5cf-fdb4-e063-6294a90a720b":
        "Amoxicillin and Clavulanate Potassium",
    "3dac2151-c2a9-49f9-8ca2-00b862c60694":
        "Azithromycin",
    "70378eba-3904-4491-9f6d-00f5d1501c4a":
        "Pantoprazole Sodium (Injection)",
    "9bae1ba3-c0da-23a2-e053-2a95a90a58ed":
        "Loratadine",
    "c5e3a37a-f6e3-43d4-a8a9-54db6c271908":
        "Omeprazole",
}

for file_path in glob.glob(os.path.join(INPUT_DIR, "*.json")):
    with open(file_path, "r", encoding="utf-8") as file:
        sections = json.load(file)

    if not sections:
        continue

    set_id = sections[0].get("set_id")
    corrected_name = DRUG_NAMES.get(set_id)

    if not corrected_name:
        print(f"WARNING: No name mapping for {set_id}")
        continue

    for section in sections:
        section["drug_name"] = corrected_name

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(sections, file, indent=2, ensure_ascii=False)

    print(f"Corrected: {corrected_name}")

print("\nMetadata correction complete.")