from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

def create_driver(download_path=None, headless=False):
    """
    Creates and configures a Chrome WebDriver.
    """
    options = webdriver.ChromeOptions()
    
    prefs = {
        "download.prompt_for_download": False,
    }
    
    if download_path:
        # Ensure absolute path
        abs_path = os.path.abspath(download_path)
        os.makedirs(abs_path, exist_ok=True)
        prefs["download.default_directory"] = abs_path
        
    options.add_experimental_option("prefs", prefs)
    
    if headless:
        options.add_argument("--headless")

    # Install/Get driver path via webdriver_manager
    # Note: The original code used ChromeDriverManager().install() which returns the path
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def set_download_path(driver, download_path):
    """
    Dynamically changes the download path for the existing driver instance.
    """
    abs_path = os.path.abspath(download_path)
    os.makedirs(abs_path, exist_ok=True)
    
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": abs_path
    })

