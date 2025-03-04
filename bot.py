import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback  # For error reporting

# ✅ Fetch Credentials from GitHub Secrets
CJ_USERNAME = os.getenv("CJ_USERNAME")
CJ_PASSWORD = os.getenv("CJ_PASSWORD")
CJ_LOGIN_URL = "https://www.cjdropshipping.com/login.html"

ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_LOGIN_URL = "https://alphapicks.odoo.com/web/login?redirect=%2Fodoo%3F"

# ✅ Initialize WebDriver (Chrome)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in the background
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")  

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)  # Wait for elements to appear


def login_cj():
    """ Logs into CJ Dropshipping with error handling """
    try:
        print("🔄 Attempting to log in to CJ Dropshipping...")
        driver.get(CJ_LOGIN_URL)
        time.sleep(5)

        # Wait for login fields to appear
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
        password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        username_field.send_keys(CJ_USERNAME)
        password_field.send_keys(CJ_PASSWORD)
        password_field.send_keys(Keys.RETURN)
        
        print("✅ Successfully logged into CJ Dropshipping")
        time.sleep(5)

    except Exception as e:
        print("❌ ERROR: Failed to login to CJ Dropshipping")
        print(traceback.format_exc())


def scrape_products():
    """ Scrapes product details from CJ Dropshipping """
    try:
        print("🔄 Fetching products from CJ Dropshipping...")
        driver.get("https://app.cjdropshipping.com/myCJ.html#/productList")
        time.sleep(10)

        products = []
        product_elements = driver.find_elements(By.CLASS_NAME, "product-title")

        if not product_elements:
            print("⚠️ No products found on CJ Dropshipping. The page structure may have changed.")
            return []

        for i in range(min(5, len(product_elements))):  # Scraping first 5 products
            try:
                title = product_elements[i].text
                price_elements = driver.find_elements(By.CLASS_NAME, "product-price")

                if price_elements:
                    price = float(price_elements[i].text.replace("$", ""))
                else:
                    print(f"⚠️ Skipping product {i+1} due to missing price")
                    continue

                image = driver.find_elements(By.CLASS_NAME, "product-img")[i].get_attribute("src")

                market_price = price * 1.5
                if market_price >= 1500:
                    products.append({"title": title, "price": price, "image": image})
            except Exception as e:
                print(f"⚠️ Skipping product {i+1} due to an error: {str(e)}")

        print(f"✅ Scraped {len(products)} valid products from CJ Dropshipping")
        return products
    except Exception as e:
        print("❌ ERROR: Failed to scrape products from CJ Dropshipping")
        print(traceback.format_exc())
        return []


def login_odoo():
    """ Logs into Odoo with error handling """
    try:
        print("🔄 Logging into Odoo...")
        driver.get(ODOO_LOGIN_URL)
        time.sleep(5)

        username_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(ODOO_USERNAME)
        password_field.send_keys(ODOO_PASSWORD)
        password_field.send_keys(Keys.RETURN)
        
        print("✅ Successfully logged into Odoo")
        time.sleep(5)

    except Exception as e:
        print("❌ ERROR: Failed to login to Odoo")
        print(traceback.format_exc())


def upload_to_odoo(products):
    """ Uploads products to Odoo """
    if not products:
        print("⚠️ No products to upload. Exiting upload process.")
        return

    for product in products:
        try:
            print(f"🔄 Uploading {product['title']} to Odoo...")
            driver.get("https://alphapicks.odoo.com/web#menu_id=5&action=10")  # Odoo Product upload page
            time.sleep(5)

            driver.find_element(By.NAME, "name").send_keys(product["title"])
            driver.find_element(By.NAME, "list_price").send_keys(str(product["price"]))

            driver.find_element(By.XPATH, "//button[contains(text(),'Save')]").click()
            time.sleep(3)

            print(f"✅ Successfully uploaded {product['title']} to Odoo")
        except Exception as e:
            print(f"❌ ERROR: Failed to upload {product['title']} to Odoo")
            print(traceback.format_exc())


def main():
    try:
        login_cj()
        products = scrape_products()
        login_odoo()
        upload_to_odoo(products)
    finally:
        driver.quit()  # Ensure the browser is always closed


if __name__ == "__main__":
    main()
