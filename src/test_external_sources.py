
from external_sources import search_openfda, search_pubchem

drug = "metformin"

print("\n===== TEST 1: openFDA =====")
fda_results = search_openfda(drug)

if fda_results:
    print("SUCCESS: openFDA returned", len(fda_results), "result(s).")
    print("Drug:", fda_results[0]["drug_name"])
    print("Source:", fda_results[0]["source_url"])
    print("Text preview:", fda_results[0]["text"][:400])
else:
    print("No openFDA results returned. Check the message above.")

print("\n===== TEST 2: PubChem =====")
pubchem_results = search_pubchem(drug)

if pubchem_results:
    print("SUCCESS: PubChem returned", len(pubchem_results), "result(s).")
    print(pubchem_results[0]["text"])
    print("Source:", pubchem_results[0]["source_url"])
else:
    print("No PubChem results returned. Check the message above.")
