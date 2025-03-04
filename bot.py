import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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
driver = webdriver.Chrome(options=options)

def login_cj():
    """ Logs into CJ Dropshipping """
    driver.get(CJ_LOGIN_URL)
    time.sleep(5)

    driver.find_element(By.NAME, "username").send_keys(CJ_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(CJ_PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)
    
    print("✅ Logged into CJ Dropshipping")

def scrape_products():
    """ Scrapes product details from CJ Dropshipping """
    driver.get("https://app.cjdropshipping.com/myCJ.html#/productList")
    time.sleep(5)

    products = []
    for i in range(5):  # Scraping first 5 products
        try:
            title = driver.find_elements(By.CLASS_NAME, "product-title")[i].text
            price = float(driver.find_elements(By.CLASS_NAME, "product-price")[i].text.replace("$", ""))
            image = driver.find_elements(By.CLASS_NAME, "product-img")[i].get_attribute("src")

            market_price = price * 1.5  # Example formula (Modify if needed)
            if market_price >= 1500:
                products.append({"title": title, "price": price, "image": image})
        except:
            continue

    print("✅ Scraped", len(products), "products")
    return products

def login_odoo():
    """ Logs into Odoo """
    driver.get(ODOO_LOGIN_URL)
    time.sleep(5)

    driver.find_element(By.NAME, "login").send_keys(ODOO_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(ODOO_PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)

    print("✅ Logged into Odoo")

def upload_to_odoo(products):
    """ Uploads products to Odoo """
    for product in products:
        try:
            driver.get("https://alphapicks.odoo.com/web#menu_id=5&action=10")  # Odoo Product upload page
            time.sleep(5)

            driver.find_element(By.NAME, "name").send_keys(product["title"])
            driver.find_element(By.NAME, "list_price").send_keys(str(product["price"]))

            driver.find_element(By.XPATH, "//button[contains(text(),'Save')]").click()
            time.sleep(3)

            print(f"✅ Uploaded {product['title']} to Odoo")
        except:
            print(f"❌ Failed to upload {product['title']}")

def main():
    login_cj()
    products = scrape_products()
    login_odoo()
    upload_to_odoo(products)

    driver.quit()

if __name__ == "__main__":
    main()
