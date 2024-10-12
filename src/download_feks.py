import os
import requests as re
from settings import FEK_PAGE_URL, OUTPUT_DIR
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils import load_json_data, mkdir_if_none
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE = OUTPUT_DIR / 'api_fek_retrieval_2024.json'


# Directory to save downloaded PDFs
output_dir = OUTPUT_DIR / 'pdfs'
mkdir_if_none(output_dir)


chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run browser in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-search-engine-choice-screen")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def download_pdf(url,fek_type):
    try:
        # Send a GET request to fetch the FEK Page
        response = re.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Extract the file name from the URL
        file_name = url.split("/")[-1]
        dir_path = os.path.join(output_dir, fek_type)
        mkdir_if_none(dir_path)
        file_path = os.path.join(dir_path, file_name)

        # Write the PDF to a local file
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)

        print(f"Downloaded: {file_name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        
def get_fek_pdf_url(fek_id):
    '''Load FEK's Page and returns the url of the pdf'''
    page_url = FEK_PAGE_URL + fek_id
    # Open the page URL
    driver.get(page_url)
    try:
        # Find the <a> tag with the url of the downloadable FEK pdf
        link_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn.transparent-btn.float-btn'))
        )
        driver.find_element(By.CSS_SELECTOR, 'a.btn.transparent-btn.float-btn')
        pdf_url = link_element.get_attribute('href')
        return pdf_url
    except Exception as e:
        print(f"Error: {e}")
        return None



def retrieve_fek(fek_id,fek_type):
    '''Finds the FEK pdf and downloads it'''
    pdf_url = get_fek_pdf_url(fek_id)
    if not pdf_url:
        print('fek not found')
        return
    
    download_pdf(pdf_url,fek_type)



def parseFekType(fek):
    try:
        fek_type = fek.get('search_PrimaryLabel')
        fek_type = fek_type.split(' ')[0]
    except:
        fek_type = 'unknown_fek'
    finally:
        return fek_type

if __name__ == '__main__':
    feks = load_json_data(INPUT_FILE)
    try:
        for fek in feks:
            fek_id = fek.get('search_ID')
            fek_type = parseFekType(fek)
            if fek_type != 'Α':
                #TODO also check if already downloaded
                continue
            retrieve_fek(fek_id,fek_type)
    finally:
        driver.quit()
    
    
  
