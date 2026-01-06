from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from automation.config import SUNO_EMAIL, SUNO_PASSWORD

def login_suno(driver):
    """
    Logs into Suno using the provided driver and configured credentials.
    """
    wait = WebDriverWait(driver, 20)
    
    driver.get("https://investidor.suno.com.br/login")
    
    # Cookie Banner handling
    try:
        # Short wait for cookie banner
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "hs-eu-cookie-confirmation")))
        driver.find_element(By.ID, "hs-eu-confirmation-button").click()
    except TimeoutException:
        pass # No banner, proceed

    # Login
    # Check if already logged in (redirected to dashboard or similar)
    if "investidor.suno.com.br/login" not in driver.current_url:
        # Assuming redirected effectively means logged in, or we can check for a specific element
        pass
    
    try:
        # Check if email field is present (it might not be if auto-redirected)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "user_email")))
        
        driver.find_element(By.ID, "user_email").send_keys(SUNO_EMAIL)
        driver.find_element(By.ID, "user_password").send_keys(SUNO_PASSWORD)
        driver.find_element(By.ID, "login_button").click()
        
        # Wait for login to complete
        time.sleep(5)
    except TimeoutException:
        print("Login fields not found or already logged in.")
