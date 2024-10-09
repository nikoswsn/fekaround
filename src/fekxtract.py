import pymupdf
from settings import OUTPUT_DIR
from utils import dir_ls, mkdir_if_none

INPUT_PATH = OUTPUT_DIR / "pdfs" 
OUTPUT_PATH = OUTPUT_DIR / "raw_txts" 


mkdir_if_none(OUTPUT_PATH)



feks = dir_ls(INPUT_PATH)

for fek in feks:
  doc = pymupdf.open(INPUT_PATH/fek) # open a document
  text = ""
  for page in doc: 
    text += page.get_text() 
    

  file_path = OUTPUT_PATH / f"{fek.replace('.pdf','')}.txt"

  # Write the string to the file
  with open(file_path, "w") as file:
      file.write(text)