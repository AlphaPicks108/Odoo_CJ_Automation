import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Logging setup (logs errors for debugging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Fetch Credentials from GitHub Secrets
CJ_USERNAME = os.getenv("CJ_USERNAME")
CJ_PASSWORD = os.getenv("CJ_PASSWORD")
CJ_LOGIN_URL = "https://www.cjdropshipping.com/login.html?target=aHR0cHM6Ly93d3cuY2pkcm9wc2hpcHBpbmcuY29tL3NlYXJjaC9raXRjaGVuLmh0bWw/Zmxvd0lkPTE1NjU2Mjg1ODE0NjkwNjExMjA="

ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_LOGIN_URL = "https://alphapicks.odoo.com/web/login?redirect=%2Fodoo%3F"

# ✅ Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")  # Required for GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # Fix shared memory issue
options.add_argument("--disable-blink-features=AutomationControlled")  # Hide Selenium
options.add_argument("--start-maximized")  # Maximize window
# options.add_argument("--headless")  # Disable this for debugging

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
wait = WebDriverWait(driver, 15)  # Wait up to 15 seconds for elements

def login_cj():
    """ Logs into CJ Dropshipping """
    try:
        logging.info("🔄 Attempting to log in to CJ Dropshipping...")
        driver.get(CJ_LOGIN_URL)
        time.sleep(7)  # Give time for elements to load

        # ✅ Click username field first before entering text
        username_field = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        username_field.click()
        username_field.send_keys(CJ_USERNAME)

        password_field = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        password_field.click()
        password_field.send_keys(CJ_PASSWORD)

        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign in')]")))
        sign_in_button.click()

        time.sleep(7)  # Wait for login to complete
        logging.info("✅ Successfully logged into CJ Dropshipping")

    except Exception as e:
        logging.error(f"❌ ERROR: Failed to login to CJ Dropshipping\n{e}")
        driver.save_screenshot("cj_login_error.png")  # Save screenshot if login fails

def scrape_products():
    """ Scrapes product details from CJ Dropshipping """
    try:
        logging.info("🔄 Fetching products from CJ Dropshipping...")
        driver.get("https://app.cjdropshipping.com/myCJ.html#/productList")
        time.sleep(5)

        products = []
        for i in range(5):  # Scraping first 5 products
            try:
                title = driver.find_elements(By.CLASS_NAME, "product-title")[i].text
                price = float(driver.find_elements(By.CLASS_NAME, "product-price")[i].text.replace("$", ""))
                image = driver.find_elements(By.CLASS_NAME, "product-img")[i].get_attribute("src")

                market_price = price * 1.5  # Example formula
                if market_price >= 1500:
                    products.append({"title": title, "price": price, "image": image})
            except:
                continue

        logging.info(f"✅ Scraped {len(products)} products")
        return products

    except Exception as e:
        logging.error(f"❌ ERROR: Failed to scrape products\n{e}")
        return []

def login_odoo():
    """ Logs into Odoo """
    try:
        logging.info("🔄 Logging into Odoo...")
        driver.get(ODOO_LOGIN_URL)
        time.sleep(5)

        driver.find_element(By.NAME, "login").send_keys(ODOO_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(ODOO_PASSWORD)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)

        logging.info("✅ Successfully logged into Odoo")

    except Exception as e:
        logging.error(f"❌ ERROR: Failed to login to Odoo\n{e}")
        driver.save_screenshot("odoo_login_error.png")  # Save screenshot if login fails

def upload_to_odoo(products):
    """ Uploads products to Odoo """
    if not products:
        logging.warning("⚠️ No products to upload. Exiting upload process.")
        return

    for product in products:
        try:
            driver.get("https://alphapicks.odoo.com/web#menu_id=5&action=10")  # Odoo Product upload page
            time.sleep(5)

            driver.find_element(By.NAME, "name").send_keys(product["title"])
            driver.find_element(By.NAME, "list_price").send_keys(str(product["price"]))

            driver.find_element(By.XPATH, "//button[contains(text(),'Save')]").click()
            time.sleep(3)

            logging.info(f"✅ Uploaded {product['title']} to Odoo")
        except Exception as e:
            logging.error(f"❌ ERROR: Failed to upload {product['title']} to Odoo\n{e}")

def main():
    try:
        login_cj()
        products = scrape_products()
        login_odoo()
        upload_to_odoo(products)
    except Exception as e:
        logging.error(f"❌ Critical Error in Main Process\n{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
