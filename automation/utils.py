import re
import os
import zipfile
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
from datetime import date, datetime

def url_to_filename(url: str) -> str:
    """
    Converts a URL to a safe filename.
    """
    parsed = urlparse(url)
    # Use netloc and path, replacing non-alphanumeric chars with underscore
    name = f"{parsed.netloc}{parsed.path}"
    name = re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')
    return f"{name}.html"

def clean_html(html_content: str) -> str:
    """
    Cleans HTML content by removing scripts, styles, and other unnecessary tags.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove irrelevant tags
    for tag in soup(["script", "style", "svg", "nav", "header", "footer", "aside", "form", "noscript", "iframe", "button", "input", "img"]):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove unnecessary attributes
    for tag in soup.find_all(True):
        # Keep only basic structure, removing style, onclick, etc.
        # Original code removed 'style', 'data-', 'onclick', 'class', 'id'
        for attr in list(tag.attrs.keys()): # List to avoid runtime error during iteration
             if any(attr.startswith(x) for x in ["style", "data-", "onclick", "class", "id"]):
                del tag.attrs[attr]

    return str(soup)

def zip_files_from_folder(folder_path: str, output_zip_path: str, date_filter: date = None):
    """
    Zips files from a folder. If date_filter is provided, only zips files created on that date.
    """
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check date if filter is applied
                if date_filter:
                    file_date = datetime.fromtimestamp(os.path.getctime(file_path)).date()
                    if file_date != date_filter:
                        continue
                        
                # Add to zip
                arcname = os.path.relpath(file_path, folder_path)
                z.write(file_path, arcname)
