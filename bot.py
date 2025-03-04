import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Fetch Credentials from GitHub Secrets
CJ_USERNAME = os.getenv("CJ_USERNAME")
CJ_PASSWORD = os.getenv("CJ_PASSWORD")
CJ_LOGIN_URL = "https://www.cjdropshipping.com/login.html?target=aHR0cHM6Ly93d3cuY2pkcm9wc2hpcHBpbmcuY29tL3NlYXJjaC9raXRjaGVuLmh0bWw/Zmxvd0lkPTE1NjU2Mjg1ODE0NjkwNjExMjA="

ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_LOGIN_URL = "https://alphapicks.odoo.com/web/login?redirect=%2Fodoo%3F"

# ✅ Setup Chrome WebDriver
options = Options()
options.add_argument("--headless")  # Run in the background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)  # Wait for elements to load

def login_cj():
    """ Logs into CJ Dropshipping with better handling """
    try:
        print("🔄 Attempting to log in to CJ Dropshipping...")
        driver.get(CJ_LOGIN_URL)
        time.sleep(5)  # Wait for page to load

        # ✅ Click the username & password fields before entering text
        username_field = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        username_field.click()
        username_field.send_keys(CJ_USERNAME)

        password_field = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        password_field.click()
        password_field.send_keys(CJ_PASSWORD)

        # ✅ Click the "Sign In" button
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign in')]")))
        sign_in_button.click()
        
        time.sleep(5)  # Allow login to process
        print("✅ Successfully logged into CJ Dropshipping")

    except Exception as e:
        print(f"❌ ERROR: Failed to login to CJ Dropshipping\n{e}")

def scrape_products():
    """ Scrapes product details from CJ Dropshipping """
    try:
        print("🔄 Fetching products from CJ Dropshipping...")
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
            except Exception as e:
                print(f"⚠️ Skipping product {i+1}: {e}")

        if products:
            print(f"✅ Scraped {len(products)} products")
        else:
            print("⚠️ No products found on CJ Dropshipping. The page structure may have changed.")
        
        return products

    except Exception as e:
        print(f"❌ ERROR: Failed to scrape products\n{e}")
        return []

def login_odoo():
    """ Logs into Odoo """
    try:
        print("🔄 Logging into Odoo...")
        driver.get(ODOO_LOGIN_URL)
        time.sleep(5)

        wait.until(EC.element_to_be_clickable((By.NAME, "login"))).send_keys(ODOO_USERNAME)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(ODOO_PASSWORD)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(Keys.RETURN)

        time.sleep(5)
        print("✅ Successfully logged into Odoo")

    except Exception as e:
        print(f"❌ ERROR: Failed to login to Odoo\n{e}")

def upload_to_odoo(products):
    """ Uploads products to Odoo """
    if not products:
        print("⚠️ No products to upload. Exiting upload process.")
        return
    
    for product in products:
        try:
            driver.get("https://alphapicks.odoo.com/web#menu_id=5&action=10")  # Odoo Product upload page
            time.sleep(5)

            driver.find_element(By.NAME, "name").send_keys(product["title"])
            driver.find_element(By.NAME, "list_price").send_keys(str(product["price"]))
            driver.find_element(By.XPATH, "//button[contains(text(),'Save')]").click()
            time.sleep(3)

            print(f"✅ Uploaded {product['title']} to Odoo")

        except Exception as e:
            print(f"❌ Failed to upload {product['title']}: {e}")

def main():
    login_cj()
    products = scrape_products()
    login_odoo()
    upload_to_odoo(products)

    driver.quit()
    print("✅ Script completed successfully.")

if __name__ == "__main__":
    main()
