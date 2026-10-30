
import requests

OPENFDA_URL = "https://api.fda.gov/drug/label.json"
PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

SOURCE_LINKS = {
    "DailyMed": "https://dailymed.nlm.nih.gov/dailymed/",
    "openFDA Drug Labels": "https://open.fda.gov/apis/drug/label/",
    "Drugs@FDA": "https://www.accessdata.fda.gov/scripts/cder/daf/",
    "FDA Drug Safety": "https://www.fda.gov/drugs/drug-safety-and-availability",
    "CDSCO India": "https://cdsco.gov.in/",
    "Indian Pharmacopoeia Commission": "https://iponline.ipc.gov.in/",
    "PubChem": "https://pubchem.ncbi.nlm.nih.gov/",
}


def search_openfda(drug_name, limit=3):
    """Search publicly accessible FDA drug-label records."""
    try:
        response = requests.get(
            OPENFDA_URL,
            params={
                "search": f'openfda.generic_name:"{drug_name}"',
                "limit": limit,
            },
            timeout=15,
        )

        if response.status_code == 404:
            return []

        response.raise_for_status()
        records = response.json().get("results", [])
        results = []
        
        for record in records:
            openfda = record.get("openfda", {})
            names = openfda.get("generic_name", [])
            if any(" AND " in name.upper() for name in names):
                continue
            # Skip combination products for single-drug searches.
            if len(names) != 1:
                continue
            
       

            results.append({
                "source": "openFDA Drug Labels",
                "drug_name": ", ".join(
                    openfda.get("generic_name", [drug_name])
                ),
                "text": "\n".join(
                    f"{section}: {' '.join(value) if isinstance(value, list) else value}"
                    for section, value in record.items()
                    if section != "openfda"
                    and isinstance(value, (str, list))
                ),
                "source_url": SOURCE_LINKS["openFDA Drug Labels"],
            })

        return results

    except (requests.RequestException, ValueError) as error:
        print(f"openFDA search failed: {error}")
        return []


def search_pubchem(drug_name):
    """Retrieve basic chemical properties from PubChem."""
    try:
        response = requests.get(
            f"{PUBCHEM_URL}/compound/name/{drug_name}/property/"
            "Title,MolecularFormula,MolecularWeight/JSON",
            timeout=15,
        )

        if response.status_code == 404:
            return []

        response.raise_for_status()
        properties = response.json().get("PropertyTable", {}).get(
            "Properties", []
        )

        return [
            {
                "source": "PubChem",
                "drug_name": item.get("Title", drug_name),
                "text": (
                    f"Title: {item.get('Title', 'Unavailable')}\n"
                    f"Molecular formula: "
                    f"{item.get('MolecularFormula', 'Unavailable')}\n"
                    f"Molecular weight: "
                    f"{item.get('MolecularWeight', 'Unavailable')}"
                ),
                "source_url": SOURCE_LINKS["PubChem"],
            }
            for item in properties
        ]

    except (requests.RequestException, ValueError) as error:
        print(f"PubChem search failed: {error}")
        return []
