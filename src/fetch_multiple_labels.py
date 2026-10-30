import requests
import time

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

DRUGS = [
    "paracetamol",
    "ibuprofen",
    "cetirizine",
    "loratadine",
    "omeprazole",
    "metformin",
    "amoxicillin",
    "atorvastatin",
    "pantoprazole",
    "azithromycin",
]

def search_drug(drug_name):
    url = f"{BASE_URL}/spls.json"
    params = {
        "drug_name": drug_name,
        "page": 1,
        "pagesize": 10,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    results = response.json().get("data", [])

    if not results:
        print(f"No labels found for {drug_name}")
        return None

    # Choose the first result whose title contains the requested name.
    for item in results:
        title = item.get("title", "")
        if drug_name.lower() in title.lower():
            return item.get("setid"), title

    # Otherwise, use the first available result.
    return results[0].get("setid"), results[0].get("title")


if __name__ == "__main__":
    for drug in DRUGS:
        try:
            result = search_drug(drug)

            if result and result[0]:
                set_id, title = result
                print(f"{drug.title()}: {title}")
                print(f"Set ID: {set_id}")
            else:
                print(f"Could not identify a label for {drug}")

        except requests.RequestException as error:
            print(f"Error searching for {drug}: {error}")

        time.sleep(0.5)