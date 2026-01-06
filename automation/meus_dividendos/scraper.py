from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import date
from bs4 import BeautifulSoup
from automation.config import MEUS_DIVIDENDOS_EMAIL, MEUS_DIVIDENDOS_PASSWORD
from automation.driver import set_download_path

def download_meus_dividendos_wallet(driver, download_path):
    """
    Downloads wallet data from Meus Dividendos.
    """
    set_download_path(driver, download_path)
    wait = WebDriverWait(driver, 20)
    
    driver.get("https://portal.meusdividendos.com/login")
    
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "ng_flow_input_email")))
        email_input.send_keys(MEUS_DIVIDENDOS_EMAIL)
        
        password_input = driver.find_element(By.ID, "ng_flow_input_pass")
        password_input.send_keys(MEUS_DIVIDENDOS_PASSWORD)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button.ng_flow_user_right_inputs_btn")
        login_button.click()
        time.sleep(5)
    except TimeoutException:
        print("Login page skipped or fields not found (already logged in?).")
    
    time.sleep(5)
    
    driver.get("https://smartfolio.meusdividendos.com/beta")
    time.sleep(15)
    
    # Click Wallet
    carteira_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[contains(text(),'Carteira')]]")
    ))
    carteira_btn.click()
    time.sleep(15)
    
    # Click "Todos" tab
    todos_tab = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//li[@class='nav-item']/a[.//small[contains(text(),'Todos')]]")
    ))
    todos_tab.click()
    time.sleep(15)
    
    # Get Table
    table_container = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.table-responsive.portfolio-report-table-container")
    ))
    table_html = table_container.get_attribute("innerHTML")
    
    # Clean HTML
    soup = BeautifulSoup(table_html, "html.parser")
    for tag in soup.find_all(True):
        tag.attrs = {}
    clean_html_content = str(soup)
    
    # Save
    os.makedirs(download_path, exist_ok=True)
    today_str = date.today().strftime("%Y-%m-%d")
    filename = os.path.join(download_path, f"carteira-meus-dividendos-{today_str}.htm")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(clean_html_content)
        
    return filename
