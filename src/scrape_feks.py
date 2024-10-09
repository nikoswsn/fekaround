import requests
import json
from settings import OUTPUT_DIR, SIMPLESEARCH_URL
from utils import mkdir_if_none

YEAR="2024"

mkdir_if_none(OUTPUT_DIR)
    
# Prepare payload for the API CALL
payload = json.dumps({
  "selectYear": [
    YEAR
  ],
  "selectIssue": [],
  "documentNumber": "",
  "searchText": "",
  "datePublished": "",
  "dateReleased": ""
})

#Request to ET simplesearch api calls
response = requests.request("POST", SIMPLESEARCH_URL, data=payload)

raw_data =response.json().get('data')

data = json.loads(raw_data)

# Export the Sim
with open(OUTPUT_DIR / f"api_fek_retrieval_{YEAR}.json", 'w', encoding="utf-8") as json_file:
    json.dump(data, json_file)  

