from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchWindowException
import time
import os
from automation.utils import url_to_filename
from automation.driver import set_download_path

def download_suno_reports(driver, download_path):
    """
    Downloads Suno reports as HTML files.
    """
    set_download_path(driver, download_path)
    wait = WebDriverWait(driver, 20)
    
    driver.get("https://investidor.suno.com.br/relatorios")
    time.sleep(15) # Wait for page load
    
    container = driver.find_element(By.ID, "main-content")
    
    # Scroll to load more reports
    # Original code scrolled 8 times
    for _ in range(8):
        h0 = driver.execute_script("return arguments[0].scrollHeight", container)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        try:
            wait.until(lambda d: driver.execute_script("return arguments[0].scrollHeight", container) > h0)
        except TimeoutException:
            break
            
    # Collect reports
    locator = "div[id^='report']"
    original_window = driver.current_window_handle
    
    # Get initial count
    elements = driver.find_elements(By.CSS_SELECTOR, locator)
    elements_count = len(elements)
    
    for idx in range(elements_count):
        try:
            # Refresh elements list to avoid StaleElementReferenceException
            reports = driver.find_elements(By.CSS_SELECTOR, locator)
            if idx >= len(reports):
                break
            
            elem = reports[idx]
            
            # Check for "read" indicator using opacity
            # Read reports seem to have opacity: 0.6
            try:
                outer_html = elem.get_attribute("outerHTML")
                if "opacity: 0.6" in outer_html:
                    print(f"Skipping report {idx}: Already read (found opacity: 0.6).")
                    continue
            except Exception as e:
                print(f"Error checking report {idx}: {e}")
                pass

            # Scroll to center to avoid sticky headers covering the element
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            time.sleep(1) # Small settling time

            try:
                elem.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                 driver.execute_script("arguments[0].click();", elem)

        except StaleElementReferenceException:
            time.sleep(1)
            reports = driver.find_elements(By.CSS_SELECTOR, locator)
            if idx < len(reports):
                driver.execute_script("arguments[0].click();", reports[idx])
        
        # Switch to new window
        try:
            wait.until(lambda d: len(d.window_handles) > 1)
            new_win = next(h for h in driver.window_handles if h != original_window)
            driver.switch_to.window(new_win)
            
            time.sleep(6) # Wait for content
            
            prefix = ""
            try:
                reader = wait.until(EC.presence_of_element_located((By.ID, "readerData")))
                html = reader.get_attribute("innerHTML")
            except TimeoutException:
                try:
                    radar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".elementor.radar-fii")))
                    html = radar.get_attribute("innerHTML")
                except TimeoutException:
                    html = driver.page_source
                    prefix = "NAO-CONSEGUI_SALVAR_"
            
            filename = os.path.join(download_path, prefix + url_to_filename(driver.current_url))
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
                
            driver.close()
            driver.switch_to.window(original_window)
        except (TimeoutException, NoSuchWindowException) as e:
            print(f"Error handling report window {idx}: {e}. Skipping.")
            # Ensure we are back on the main window just in case
            try:
                if driver.current_window_handle != original_window:
                     driver.switch_to.window(original_window)
            except NoSuchWindowException:
                driver.switch_to.window(original_window)
        
        time.sleep(2)
