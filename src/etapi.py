import requests
import json
import os
from settings import OUTPUT_DIR, SEARCHDATE_URL, SIMPLESEARCH_URL
from utils import mkdir_if_none

class ETAPI:
    def __init__(self, output_dir=OUTPUT_DIR):
        """
        Initialize the ETAPI class with an output directory.
        Creates the output directory if it does not exist.
        
        :param output_dir: Directory where the results will be saved.
        """
        self.output_dir = output_dir
        mkdir_if_none(self.output_dir)

    def save_results(self, data, filename):
        """
        Save the given data to a JSON file in the specified output directory.
        
        :param data: Data to be saved.
        :param filename: Name of the JSON file to save the data.
        """
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file)

    def __make_simplesearch_api_call(self, body):
        """
        Make a simple search API call to the SIMPLESEARCH_URL with the given request body.
        
        :param body: Request body for the simple search API call.
        :return: Parsed response data from the API call or None if the request fails.
        """
        payload = json.dumps(body)
        try:
            response = requests.request("POST", SIMPLESEARCH_URL, data=payload)
            response.raise_for_status()
            raw_data = response.json().get('data')
            data = json.loads(raw_data)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error making simple search API call: {e}")
            return None

    def simplesearch(self, body):
        """
        Perform a simple search API call and save the results if successful.
        
        :param body: Request body for the simple search API call.
        """
        data = self.__make_simplesearch_api_call(body)
        if data:
            self.save_results(data, f"simplesearch.json")

    def search_by_date_call(self, date):
        """
        Make a search by date API call to the SEARCHDATE_URL with the specified date.
        
        :param date: The date to be used for the search in the format YYYY-MM-DD.
        :return: Parsed response data from the API call or None if the request fails.
        """
        payload = json.dumps({"datePublished": date})
        try:
            response = requests.request("POST", SEARCHDATE_URL, data=payload)
            response.raise_for_status()
            raw_data = response.json().get('data')
            data = json.loads(raw_data)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error making search by date API call: {e}")
            return None

    def search_by_date(self, date):
        """
        Perform a search by date API call and save the results if successful.
        
        :param date: The date to be used for the search in the format YYYY-MM-DD.
        """
        data = self.search_by_date_call(date)
        if data:
            self.save_results(data, f"date_{date}.json")

# Example usage
if __name__ == "__main__":
    et_api = ETAPI()
    # Example request body for a simple search
    simple_search_body = {
            "selectYear": [
                "2024"
            ],
            "selectIssue": [],
            "documentNumber": "",
            "searchText": "",
            "datePublished": "",
            "dateReleased": ""
        }
    et_api.simplesearch(simple_search_body)

    # Example search by date
    et_api.search_by_date("2024-10-11")