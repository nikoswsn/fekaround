import pymupdf
from settings import OUTPUT_DIR
from utils import dir_ls, mkdir_if_none
from os import path

FEK_TYPE = "Α" #subdirectory name in raw_txts
INPUT_PATH = OUTPUT_DIR / "pdfs" / FEK_TYPE
TXT_DIR = OUTPUT_DIR / "raw_txts"
OUTPUT_PATH = TXT_DIR / FEK_TYPE

mkdir_if_none(TXT_DIR)
mkdir_if_none(OUTPUT_PATH)



feks = dir_ls(INPUT_PATH)

for fek in feks:
  output_filepath = OUTPUT_PATH / f"{fek.replace('.pdf','')}.txt"
  if path.exists(output_filepath):
    continue
  doc = pymupdf.open(INPUT_PATH/fek) # open a document
  text = ""
  for page in doc: 
    text += page.get_text() 
    
  

  # Write the string to the file
  with open(output_filepath, "w") as file:
      file.write(text)