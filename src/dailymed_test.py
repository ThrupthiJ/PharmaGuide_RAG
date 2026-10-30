import requests

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"


def search_drug(drug_name):
    url = f"{BASE_URL}/spls.json"

    params = {
        "drug_name": drug_name,
        "page": 1,
        "pagesize": 5,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        result = response.json()

        records = result.get("data", [])

        if not records:
            print(f"No drug labels found for: {drug_name}")
            return

        for record in records:
            print("Drug label:", record.get("title"))
            print("Set ID:", record.get("setid"))
            print("-" * 50)

    except requests.RequestException as error:
        print("DailyMed connection failed:", error)

    except ValueError:
        print("Could not parse the API response.")


if __name__ == "__main__":
    search_drug("ibuprofen")