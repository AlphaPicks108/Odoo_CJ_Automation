import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Fetch Credentials from GitHub Secrets
CJ_USERNAME = os.getenv("CJ_USERNAME")
CJ_PASSWORD = os.getenv("CJ_PASSWORD")
CJ_LOGIN_URL = "https://www.cjdropshipping.com/login.html?target=aHR0cHM6Ly93d3cuY2pkcm9wc2hpcHBpbmcuY29tL3NlYXJjaC9raXRjaGVuLmh0bWw/Zmxvd0lkPTE1NjU2Mjg1ODE0NjkwNjExMjA="

ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_LOGIN_URL = "https://alphapicks.odoo.com/web/login?redirect=%2Fodoo%3F"

# ✅ Initialize WebDriver (Chrome)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in the background (remove for debugging)
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
driver = webdriver.Chrome(options=options)

def login_cj():
    """ Logs into CJ Dropshipping """
    driver.get(CJ_LOGIN_URL)
    time.sleep(5)  # Wait for the page to load

    wait = WebDriverWait(driver, 15)

    # Click on the username field before typing
    username_field = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    ActionChains(driver).move_to_element(username_field).click().perform()
    username_field.send_keys(CJ_USERNAME)

    # Click on the password field before typing
    password_field = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    ActionChains(driver).move_to_element(password_field).click().perform()
    password_field.send_keys(CJ_PASSWORD)

    # Click the Sign-In button
    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign in')]")))
    sign_in_button.click()

    time.sleep(5)  # Wait for login to complete

    print("✅ Logged into CJ Dropshipping (if no errors)")

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

    wait = WebDriverWait(driver, 15)

    # Enter login details
    login_field = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
    login_field.send_keys(ODOO_USERNAME)

    password_field = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    password_field.send_keys(ODOO_PASSWORD)

    # Click login button
    password_field.send_keys(Keys.RETURN)
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
    try:
        login_cj()
        products = scrape_products()

        if not products:
            print("⚠️ No products found on CJ Dropshipping. Exiting.")
            return

        login_odoo()
        upload_to_odoo(products)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
