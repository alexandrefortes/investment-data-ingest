from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from urllib.parse import urlparse
from automation.utils import url_to_filename, clean_html
from automation.driver import set_download_path
from datetime import date

def download_suno_wallets(driver, download_path):
    """
    Downloads Suno wallets as HTML files.
    """
    set_download_path(driver, download_path)
    wait = WebDriverWait(driver, 20)
    today_str = date.today().strftime("%Y-%m-%d")
    
    driver.get("https://investidor.suno.com.br/carteiras")
    time.sleep(15)
    
    # Scroll logic
    scroll_container = driver.find_element(By.ID, "main-content")
    for i in range(3):
        current_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        try:
            wait.until(lambda d: driver.execute_script("return arguments[0].scrollHeight", scroll_container) > current_height)
        except TimeoutException:
            break
            
    # Find links
    elements = driver.find_elements(By.CSS_SELECTOR, "a.WmCKBGPeU3I8A1eENMyG")
    hrefs = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
    
    carteiras_url = "https://investidor.suno.com.br/carteiras"
    
    for link_href in hrefs:
        parsed_url = urlparse(link_href)
        driver.get(link_href)
        time.sleep(4)
        
        file_prefix = ""
        
        if parsed_url.path == "/carteiras/internacional":
            all_divs = driver.find_elements(By.CSS_SELECTOR, "div.OBL8xjDqKulPUiJR2xLn")
            # Indexes 0 to 4
            for index in [0, 1, 2, 3, 4]:
                if index >= len(all_divs): break
                div_to_click = all_divs[index]
                driver.execute_script("arguments[0].click();", div_to_click)
                time.sleep(3)
                
                path_realtime = urlparse(driver.current_url).path
                _save_wallet_content(driver, download_path, path_realtime, today_str, wait)
                
            driver.get(carteiras_url)
            
        elif parsed_url.path == "/carteiras/fundos":
            all_divs = driver.find_elements(By.CSS_SELECTOR, "div.aitB5h9xFRt1CAXd2E8t.YxNKF3awfZ4s67CWXRjA > div.OBL8xjDqKulPUiJR2xLn")
            
            for div_to_click in all_divs:
                driver.execute_script("arguments[0].click();", div_to_click)
                time.sleep(3)
                path_realtime = urlparse(driver.current_url).path
                _save_wallet_content(driver, download_path, path_realtime, today_str, wait)
            
            driver.get(carteiras_url)
            
        else:
            path_realtime = parsed_url.path
            _save_wallet_content(driver, download_path, path_realtime, today_str, wait)
            driver.back()
            time.sleep(2)

def _save_wallet_content(driver, download_path, path_realtime, today_str, wait):
    """Helper to extract and save wallet content"""
    file_prefix = ""
    try:
        main_content = wait.until(EC.presence_of_element_located((By.ID, "main-content")))
        time.sleep(3)
        html_content = main_content.get_attribute("innerHTML")
    except TimeoutException:
        html_content = driver.page_source
        file_prefix = "NAO-CONSEGUI_SALVAR_"
    
    cleaned_html = clean_html(html_content)
    
    filename = os.path.join(
        download_path,
        f"{file_prefix}carteira-{today_str}-{url_to_filename(path_realtime)}"
    )
    
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(cleaned_html)
