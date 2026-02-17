from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
import os
import traceback

# A few helper functions
# Create the optimized driver (loads fast, limits images)
def create_optimized_driver():
    # Use Options class to customize WebDriver
    options = Options()
    # Wait for DOM to be interactive (instead of all resources to downloaded)
    options.page_load_strategy = 'eager'
    
    # Block all images, background networking and extensions
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-extensions')
    
    driver = webdriver.Chrome(options=options)
    
    # Longer timeout for initial load
    driver.set_page_load_timeout(60)
    
    return driver

def take_screenshot(name):
    # Create screenshot folder, name screenshot images
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    filename = f"screenshots/{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved as: {filename}")
    return filename

# Step counter class to count step number automatically
class StepCounter:
    def __init__(self):
        self.step = 1
    
    def print_step(self, message):
        print(f"\n--- Step {self.step}: {message} ---")
        self.step += 1

# Initialize driver and wait
user_email = input("Enter email: ")
driver = create_optimized_driver()
driver.maximize_window()
wait = WebDriverWait(driver, 20)
website_main = "https://eu.levenhuk.com/"
test_phone = "+79444444444"

# Choose random sku
def choose_sku():
    # Dictionary with 2 price classes
    items = {
    "skus_under_70": [83836, 83820, 84547, 84545, 83089],
    "skus_70_plus": [84558, 84638, 84087, 83842, 85574]
    }
    # Price class 0 - under 70, price class 1 - 70+ EU
    price_class = random.randint(0, 1)
    item_num = random.randint(0, 4)
    if price_class == 1:
        sku = items["skus_under_70"][item_num]
    else:
        sku = items["skus_70_plus"][item_num]
    return(sku)



