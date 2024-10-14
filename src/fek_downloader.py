import os
import requests
from settings import FEK_PAGE_URL, OUTPUT_DIR
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils.utils import load_json_data, mkdir_if_none, dir_ls, read_txt_lines, save_txt
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymupdf
from os import path
import re


class FEKDownloader:
    """
    A class to handle downloading and extracting text from FEK PDF files.
    
    :param input_file (str): Path to the JSON file containing FEK data.
    :param pdf_dir (str): Directory to save downloaded PDFs.
    :param raw_txt_dir (str): Directory to save extracted text from PDFs.
    """
    
    def __init__(self, input_file, pdf_dir="pdfs", raw_txt_dir="raw_txts", clean_txt_dir="cleaned_txt"):
        """
        Initializes the FEKDownloader with paths for input, output directories, and sets up Chrome options.

        Args:
        input_file (str): JSON file containing FEK data.
        raw_txt_dir (str, optional): Directory to save downloaded PDFs. Defaults to "pdfs".
        """
        self.input_file = OUTPUT_DIR / input_file
        self.pdf_dir = OUTPUT_DIR / pdf_dir
        self.raw_txt_dir = OUTPUT_DIR / raw_txt_dir
        self.clean_txt_dir = OUTPUT_DIR / clean_txt_dir
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        mkdir_if_none(self.pdf_dir)
        mkdir_if_none(self.raw_txt_dir)
        
    def __del__(self):
        """
        Destructor to close the WebDriver when the object is destroyed.
        """
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing Chrome driver: {e}")
                
    def download_pdf(self, url, fek_type):
        """
        Downloads a PDF from the given URL and saves it to the specified directory.

        :param url (str): URL to download the PDF from.
        :param fek_type (str): Type of FEK to determine the directory.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            file_name = url.split("/")[-1]
            dir_path = os.path.join(self.pdf_dir, fek_type)
            mkdir_if_none(dir_path)
            file_path = os.path.join(dir_path, file_name)

            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(response.content)

            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    def get_fek_pdf_url(self, fek_id):
        """
        Retrieves the URL of the downloadable PDF for a given FEK ID.

        :paramfek_id (str): The FEK ID to search for.

        Returns:
        str: URL of the downloadable PDF, or None if not found.
        """
        page_url = FEK_PAGE_URL + fek_id
        self.driver.get(page_url)
        try:
            link_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn.transparent-btn.float-btn'))
            )
            pdf_url = link_element.get_attribute('href')
            return pdf_url
        except Exception as e:
            print(f"Error: {e}")
            return None

    def retrieve_fek(self, fek_id, fek_type):
        """
        Retrieves and downloads the FEK PDF for a given FEK ID and type.

        :param fek_id (str): The FEK ID to retrieve.
        :param fek_type (str): The type of FEK.
        """
        pdf_url = self.get_fek_pdf_url(fek_id)
        if not pdf_url:
            print('fek not found')
            return

        self.download_pdf(pdf_url, fek_type)

    def parse_fek_type(self, fek):
        """
        Parses the FEK type from the FEK data.

        :param fek (dict): Dictionary containing FEK data.

        Returns:
        str: The parsed FEK type.
        """
        try:
            fek_type = fek.get('search_PrimaryLabel').split(' ')[0]
        except:
            fek_type = 'unknown_fek'
        return fek_type

    def download_feks(self):
        """
        Downloads all FEK PDFs based on the input JSON file.
        """
        feks = load_json_data(self.input_file)
        for fek in feks:
            fek_id = fek.get('search_ID')
            fek_type = self.parse_fek_type(fek)
            self.retrieve_fek(fek_id, fek_type)
            
    def __clean_disclaimer(self, lines):
        disclaimer_start = """ΤαχυδρομικήΔιεύθυνση:Καποδιστρίου34,τ.κ.10432,Αθήνα"""
        text = ""
        for line in lines:
            if disclaimer_start in line.replace(" ", ""):
                return text
            text += line
        return text
    
    def __clean_seperated_words(self, txt):
        return txt.replace(" -\n", "").replace("-\n","").replace(" \n", " ")
    
    def __clean_header(self, lines):
        text = ""
        skip_line = False
        for line in lines:
            if skip_line:
                skip_line = False
                continue
            header_variants = ["ΕΦΗΜΕΡΙ∆Α TΗΣ ΚΥΒΕΡΝΗΣΕΩΣ", "ΕΦΗΜΕΡΙΔΑ TΗΣ ΚΥΒΕΡΝΗΣΕΩΣ"]
            for var in header_variants:
                if var in line:
                    skip_line = True
                    break
            if skip_line:
                continue
            
            text += line + "\n"
        return text
    
    def __clean_lines(self, lines):
        text= ""
        start_with = ["ΤεύχοςA’", "Αρ.Φύλλου", "ΤΕΥΧΟΣΠΡΩΤΟ"]
        equals = [ "ΕΦΗΜΕΡΙ∆Α", "ΤΗΣΚΥΒΕΡΝΗΣΕΩΣ", "ΤΗΣΕΛΛΗΝΙΚΗΣ∆ΗΜΟΚΡΑΤΙΑΣ" ]
        skip_line = False
        for line in lines:
            skip_line = False
            for var in start_with:
                if line.replace(" ","").startswith(var):
                    skip_line = True
                    break
            for var in equals:
                if line.replace(" ","") == var:
                    skip_line = True
                    break
            if skip_line:
                continue
            text += line + "\n"
        return text
                 
    def clean_text(self):
        fek_types = [f for f in os.listdir(self.raw_txt_dir) if path.isdir(self.raw_txt_dir / f)]

        for fek_type in fek_types:
            input_path = self.raw_txt_dir / fek_type
            output_path = self.clean_txt_dir / fek_type
            mkdir_if_none(output_path)

            feks = dir_ls(input_path)
            for fek in feks:
                output_filepath = output_path / f"{fek.replace('.txt','_cleaned')}.txt"

                lines = read_txt_lines(input_path / fek)
                text = self.__clean_disclaimer(lines)
                text = self.__clean_header(text.split("\n"))
                text = self.__clean_lines(text.split("\n"))

                clean_text =""
                for line in text.split('\n'):
                    # Regex to identify lines that are likely part of a table
                    pattern = r'^(?!.*[\u0370-\u03FF\u1F00-\u1FFF]).*$'

                    if not re.match(pattern, line):
                        clean_text += line + "\n"
                text = self.__clean_seperated_words(clean_text)
                save_txt(text, output_filepath)
                
    def extract_text_from_pdfs(self):
        """
        Extracts text from all downloaded FEK PDFs and saves them as text files.
        """
        # Get all subdirectories inside the pdf_dir
        fek_types = [f for f in os.listdir(self.pdf_dir) if path.isdir(self.pdf_dir / f)]

        for fek_type in fek_types:
            input_path = self.pdf_dir / fek_type
            output_path = self.raw_txt_dir / fek_type
            mkdir_if_none(output_path)

            feks = dir_ls(input_path)
            for fek in feks:
                output_filepath = output_path / f"{fek.replace('.pdf','')}.txt"

                doc = pymupdf.open(input_path / fek)
                pages = [page.get_text("text") for page in doc]
                text = '\n'.join(pages)

                with open(output_filepath, "w") as file:
                    file.write(text)

        




if __name__ == '__main__':
    #To run the example below you first have to run src/etapi.py with the date "2024-10-14"
    handler = FEKDownloader("date_2024-10-14.json", "pdfs_14", "raw_txts_14", "clean_txts_14")
    handler.download_feks()
    handler.extract_text_from_pdfs()
    handler.clean_text()
