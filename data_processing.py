import os

from config import ORIGINAL_DATA_DIR, PROCESSED_DATA_DIR

# TODO: take the downloaded data from ORIGINAL_DATA_DIR,
# clean the documents (extract text information,
# remove boilerplate, etc.) and save the cleaned data
# to PROCESSED_DATA_DIR in the following format.

# --- PROCESSED_DATA_DIR
# ------ {ticker 1}_{earliest year}
# --------- content.txt
# ------ {ticker 1}_{earliest year + 1}
# --------- content.txt
# ...
# ------ {ticker 1}_{latest year}
# --------- content.txt
# ------ {ticker 2}_{earliest year}
# --------- content.txt
# ------ {ticker 2}_{earliest year + 1}
# --------- content.txt
# ...
# ------ {ticker 2}_{latest year}
# --------- content.txt
# ...
# ------ {ticker 10}_{earliest year}
# --------- content.txt
# ------ {ticker 10}_{earliest year + 1}
# --------- content.txt
# ...
# ------ {ticker 10}_{latest year}
# --------- content.txt

# In terms of implementation, this part is the most flexible.
# The bare minimum for this part (valued 5 points) is saving
# the original documents in the format described before
# without processing them. The remaining 10 points will be given
# for the attempts to clean the data.

# There is no objective criteria for the quality of cleaning.
# As the first thing to try, we would suggest removing
# html tags. However, tables in this case become a mess,
# and it is very likely that an LLM would do better if
# the html structure was preserved.

# Please make reasonable efforts to manipulate HTML tags effectively,
# remove unnecessary boilerplate content, and explore other
# preprocessing techniques as deemed appropriate.


import os
import re
from bs4 import BeautifulSoup

# Directories
ORIGINAL_DATA_DIR = "./data/original/sec-edgar-filings"
# PROCESSED_DATA_DIR = "./data/processed"

def clean_html_content(file_content):
    soup = BeautifulSoup(file_content, 'lxml')
    
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    cleaned_text = soup.get_text(separator='\n')

    # Stop processing at the cutoff string
    cutoff_string = "XBRL INSTANCE DOCUMENT"
    cutoff_index = cleaned_text.find(cutoff_string)
    if cutoff_index != -1:
        cleaned_text = cleaned_text[:cutoff_index]

    cleaned_text = '\n\n'.join(
        [re.sub(r'\s+', ' ', paragraph).strip() for paragraph in cleaned_text.split('\n') if paragraph.strip()]
    )

    # paragraphs = cleaned_text.split("\n\n")
    # print(len(paragraphs))
    # print(len(paragraphs[30]))
    # print((paragraphs[30]))
    return cleaned_text

def extract_ticker_and_year(path):

    parts = path.split(os.sep)
    ticker = parts[-4]  # Ticker is 4 levels up from the file
    folder_name = parts[-2]  # Folder name contains year info
    match = re.search(r"-(\d{2})-", folder_name)  # Extract year from folder name
    if match:
        year = "20" + match.group(1)  # Convert to full year (e.g., -11- -> 2011)
        return ticker, year
    return ticker, None

def process_files():
    
    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)
    
    for root, dirs, files in os.walk(ORIGINAL_DATA_DIR):
        for file in files:
            if file.endswith(".txt"):  # Process only relevant file types
                file_path = os.path.join(root, file)
                
                # Extract ticker and year from directory structure
                ticker, year = extract_ticker_and_year(file_path)
                if not year:
                    print(f"Year could not be determined for file: {file_path}")
                    continue
                
                print(f"Processing file: {file_path}")
                output_dir = os.path.join(PROCESSED_DATA_DIR, f"{ticker}_{year}")
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                output_file_path = os.path.join(output_dir, "content.txt")
                
                # Read, clean, and write content
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                cleaned_content = clean_html_content(raw_content)
                
                with open(output_file_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(cleaned_content)

process_files()




# Possible scores:
# [10 pts]         The processed documents is stored
#                 in the aforementioned format.
# [5 pts]       The format for the processed data
#                 is not preserved.
# [up to +10 pts] Some level of cleaning is done.
