import requests
import json
import os
import time
import xml.etree.ElementTree as ET

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
NAMESPACE = {"hl7": "urn:hl7-org:v3"}

DRUG_LABELS = {
    "paracetamol": "bf001b70-6164-1ec9-e053-2a95a90a1274",
    "ibuprofen": "0daf1be9-ea38-461e-e063-6394a90a7954",
    "cetirizine": "113e66f1-b922-8533-e063-6294a90ab30e",
    "loratadine": "9bae1ba3-c0da-23a2-e053-2a95a90a58ed",
    "omeprazole": "c5e3a37a-f6e3-43d4-a8a9-54db6c271908",
    "metformin": "056072d8-6228-4914-831d-ee7c0661b742",
    "amoxicillin_clavulanate": "36efc48d-f5cf-fdb4-e063-6294a90a720b",
    "atorvastatin": "10e766cc-c3fd-4584-a0d7-652c516e828c",
    "pantoprazole": "70378eba-3904-4491-9f6d-00f5d1501c4a",
    "azithromycin": "3dac2151-c2a9-49f9-8ca2-00b862c60694",
}


def extract_label(set_id):
    url = f"{BASE_URL}/spls/{set_id}.xml"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    title_element = root.find("hl7:title", NAMESPACE)
    drug_name = (
        " ".join("".join(title_element.itertext()).split())
        if title_element is not None
        else "Unknown drug"
    )

    version_element = root.find("hl7:versionNumber", NAMESPACE)
    version = (
        version_element.get("value")
        if version_element is not None
        else None
    )

    effective_element = root.find("hl7:effectiveTime", NAMESPACE)
    effective_date = (
        effective_element.get("value")
        if effective_element is not None
        else None
    )

    sections = []

    for section in root.findall(".//hl7:section", NAMESPACE):
        title = section.find("hl7:title", NAMESPACE)
        text_element = section.find("hl7:text", NAMESPACE)

        if text_element is None:
            continue

        section_name = (
            " ".join("".join(title.itertext()).split())
            if title is not None
            else "Untitled section"
        )

        text = " ".join("".join(text_element.itertext()).split())

        if not text:
            continue

        sections.append({
            "drug_name": drug_name,
            "set_id": set_id,
            "version": version,
            "effective_date": effective_date,
            "section": section_name,
            "text": text,
            "source_url": url,
        })

    if not sections:
        raise ValueError(f"No readable sections found for {set_id}")

    return sections


def main():
    os.makedirs("data/processed", exist_ok=True)

    successful = 0

    for drug, set_id in DRUG_LABELS.items():
        output_file = f"data/processed/{drug}_{set_id}.json"

        # Avoid downloading a label again if it already exists.
        if os.path.exists(output_file):
            print(f"Already downloaded: {drug}")
            successful += 1
            continue

        try:
            sections = extract_label(set_id)

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(
                    sections,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"Downloaded: {drug} — {len(sections)} sections")
            successful += 1

        except (
            requests.RequestException,
            ET.ParseError,
            ValueError,
        ) as error:
            print(f"Failed: {drug} — {error}")

        time.sleep(0.5)

    print(f"\nCompleted: {successful}/{len(DRUG_LABELS)} labels processed.")


if __name__ == "__main__":
    main()