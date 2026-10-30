import requests
import json
import os
import xml.etree.ElementTree as ET

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

SET_ID = "0daf1be9-ea38-461e-e063-6394a90a7954"

NAMESPACE = {"hl7": "urn:hl7-org:v3"}


def fetch_drug_label(set_id):
    url = f"{BASE_URL}/spls/{set_id}.xml"

    try:
        # Do not set an Accept header.
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        # Extract the document title.
        title_element = root.find("hl7:title", NAMESPACE)
        drug_name = (
            "".join(title_element.itertext()).strip()
            if title_element is not None
            else "Unknown drug"
        )

        # Extract document version/date metadata.
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

        documents = []

        # Extract sections while preserving section titles.
        for section in root.findall(".//hl7:section", NAMESPACE):
            title = section.find("hl7:title", NAMESPACE)

            if title is not None:
                section_name = " ".join(
                    "".join(title.itertext()).split()
                )
            else:
                section_name = "Untitled section"

            text_element = section.find("hl7:text", NAMESPACE)

            if text_element is None:
                continue

            text = " ".join(
                "".join(text_element.itertext()).split()
            )

            if not text:
                continue

            documents.append({
                "drug_name": drug_name,
                "set_id": set_id,
                "version": version,
                "effective_date": effective_date,
                "section": section_name,
                "text": text,
                "source_url": url,
            })

        if not documents:
            print("No readable sections found.")
            return

        os.makedirs("data/processed", exist_ok=True)

        output_file = f"data/processed/{set_id}.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(documents, file, indent=2, ensure_ascii=False)

        print("Drug label retrieved successfully!")
        print("Drug:", drug_name)
        print("Set ID:", set_id)
        print("Sections extracted:", len(documents))
        print("Saved to:", output_file)

        print("\nExtracted sections:")
        for document in documents:
            print("-", document["section"])

    except requests.RequestException as error:
        print("DailyMed request failed:", error)

    except ET.ParseError as error:
        print("Could not parse the XML:", error)


if __name__ == "__main__":
    fetch_drug_label(SET_ID)