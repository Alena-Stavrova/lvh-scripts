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

def choose_address():
    # Define a list of shipping addresses
    shipping_addresses = [
    {
        'country': 'Finland',
        'city': 'Oulu',
        'address': 'Aleksanterinkatu 46',
        'postal_code': '90120'
    },
    {
        'country': 'Greece',
        'city': 'Thessaloniki', 
        'address': 'Kassandrou 37',
        'postal_code': '54633'
    },
    {
        'country': 'Slovenia',
        'city': 'Maribor',
        'address': 'Komenskega ulica 2',
        'postal_code': '2000'
    }
]
    address = shipping_addresses[random.randint(0,2)] 
    return(address) #returns a dictionary

def extract_price(price_text):
    # Extract numeric price from text
    # Remove all characters except digits and the comma (EU format)
    clean_text = re.sub(r'[^\d,]', '', price_text)
    # Replace comma with dot
    clean_text = clean_text.replace(',', '.')
    
    try:
        return float(clean_text)
    except ValueError:
        return None
    
def get_total_price():
    # Extract the total price from the Cart price block
    try:
        price_text = driver.find_element(By.CLASS_NAME, 'cart-panel__price').text
        price = extract_price(price_text)
        if price is not None:
            return price               
             
        print("✗ Could not find total price on page")
        return None
        
    except Exception as e:
        print(f"✗ Error extracting price: {str(e)}")
        return None

def close_cookie_popup():
    # Close the cookie consent popup 
    try:
        accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".cky-btn.cky-btn-accept"))
        )
        accept_button.click()
        print("Cookie popup closed")
        time.sleep(1)
        return True    
     
    except Exception as e:
        print(f"Error handling cookie popup: {str(e)}")
        return False

def search_for_sku(sku):
    # Find item by SKU search
    try:
        print("Navigating to main page...")
        driver.get(website_main)
        time.sleep(3)
        
        print("Opening search box...")
        search_box = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "header__search")))
        search_box.click()
        time.sleep(1)
        
        print("Entering SKU...")
        search_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "search__input")))
        search_input.clear()
        search_input.send_keys(str(sku))
       
        print("Submitting search...")
        search_input.send_keys(Keys.ENTER)       
        print("Waiting for results to load...")

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, ".b-48.pb-md-24"))
            )
        except:
            time.sleep(5)

        # Find card SKU line, like "Product ID: 83836"
        card_sku_elem = driver.find_element(By.CLASS_NAME, 'catalog-card__article')
        card_sku = int(card_sku_elem.text[-6:])
        print(f"SKU on the product card is: {card_sku}")
        
        # Scroll to the element to take screenshot
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_sku_elem)
        time.sleep(2)
        take_screenshot("search_results")

        # Check if item is out of stock (maybe add price verification later)
        item_price = driver.find_element(By.CLASS_NAME, 'catalog-card__price').text
        if item_price == "Out of stock":
            # Just add a warning for now. Later can reselect item
            print("WARNING: Can't add this item to cart")
                  
        if sku == card_sku:        
            print("✓ Search completed successfully")
            return True
        else:
            print(f"✗ First found item doesn't match the search: looked for {sku}, firs item is {card_sku}")
            return False
        
    except Exception as e:
        print(f"✗ Search failed: {str(e)}")
        take_screenshot("search_error")
        return False

def get_offer_id(sku):
    # Offer ID is in data-id
    try:
        print(f"Finding offer ID for SKU: {sku}")
        
        # Find the catalog-card container that contains SKU text and get its data-id
        offer_id_xpath = f"//div[contains(@class, 'catalog-card') and .//div[contains(@class, 'catalog-card__article') and contains(text(), '{sku}')]]"
        
        container = wait.until(EC.presence_of_element_located((By.XPATH, offer_id_xpath)))
        
        # Get the offer ID from data-id attribute
        offer_id = container.get_attribute('data-id')
        
        if offer_id:
            print(f"✓ Found offer ID: {offer_id}")
            return int(offer_id)
        else:
            print("✗ No data-id attribute found on container")
            return None
            
    except Exception as e:
        print(f"✗ Error finding offer ID: {str(e)}")
        return None

def add_to_cart_via_api(offer_id, quantity=1):
    # Simple API call - no UI updates attempted, relies on page refresh to update the cart
    try:
        print(f"Adding offer {offer_id} to cart via API...")
        
        script = f"""
            fetch('/rest/methods/user/basket/change', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{offerId: {offer_id}, quantity: "{quantity}"}})
            }})
            .then(response => response.json())
            .then(data => {{
                console.log('API Response:', data);
                // Store success state for verification
                window.lastCartAdd = {{
                    success: true,
                    offerId: {offer_id},
                    timestamp: Date.now()
                }};
            }})
            .catch(error => {{
                console.error('API Error:', error);
                window.lastCartAdd = {{success: false, error: error.message}};
            }});
        """
        
        driver.execute_script(script)
        time.sleep(2)  # Wait for API call
        
        # Verify it worked
        check_script = """
            return window.lastCartAdd || {success: false, error: 'No response'};
        """
        result = driver.execute_script(check_script)
        
        if result.get('success'):
            print(f"✓ API call successful for offer {offer_id}")
            return True
        else:
            print(f"✗ API call failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error in API call: {e}")
        return False

def navigate_to_cart_directly():
    # Navigate to the cart page directly by URL
    try:
        cart_url = website_main + "basket/"
        print(f"Navigating to cart URL: {cart_url}")
        
        driver.get(cart_url)
        time.sleep(3)
        
        # Check if we're on a cart page
        current_url = driver.current_url.lower()
        if "basket" in current_url:
            print("✓ Successfully navigated to cart page")
            return True
        else:
            print(f"Not on cart page. Current URL: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"✗ Failed to navigate to cart: {str(e)}")
        take_screenshot("cart_navigation_error")
        return False

def check_cart_contents(sku, expected_quantity=1):
    # Verify our item is in the basket
    cart_items = driver.find_elements(By.CSS_SELECTOR, 
        "div[class*='cart-table__item'][id^='basket-item-']")
    total_qty = 0
    found = False
    
    for cart_item in cart_items:  # cart_item is the whole DIV for a basket item
        # Check if this cart item has our SKU
        if str(sku) in cart_item.text:
            found = True
            # Get quantity directly in element counter
            qty_input = cart_item.find_element(By.CSS_SELECTOR, 
                "[data-entity='basket-item-quantity-field']")
            qty = int(qty_input.get_attribute('value'))
            total_qty += qty
            print(f"✓ Found SKU {sku}, quantity: {qty}")
    
    if not found:
        print(f"✗ SKU {sku} not found")
        return False
    
    print(f"Total quantity: {total_qty}, Expected: {expected_quantity}")
    return total_qty == expected_quantity

def proceed_to_checkout():
    # Click the checkout button, verify Basket > Order page
    try:
        checkout_button = driver.find_element(By.CSS_SELECTOR, "[data-entity='basket-checkout-button']")
        if checkout_button and checkout_button.is_displayed():
            print(f"Found checkout button")
                                
        if not checkout_button:
            raise Exception("Could not find checkout button")
        
        print("Clicking checkout button...")
        checkout_button.click()
        
        # Wait for the order page to load
        print("Waiting for order page to load...")
        WebDriverWait(driver, 5).until(
            EC.url_contains("order")
        )
        
        # Verify we're on the order page
        current_url = driver.current_url.lower()
        if "order" in current_url:
            print(f"✓ Successfully navigated to order page: {driver.current_url}")
            return True
        else:
            print(f"✗ Not on order page. Current URL: {driver.current_url}")
            take_screenshot("not_on_order_page")
            return False
        
    except Exception as e:
        print(f"✗ Failed to proceed to checkout: {str(e)}")
        take_screenshot("checkout_error")
        return False

def select_payment_option():
    # Only available for items 70+ EU (otherwise TBD, default)
    try:
        print("Selecting payment option...")
        
        # Define payment options with their corresponding IDs (equal probability)
        payment_options = {
            "Bank transfer": "ID_PAY_SYSTEM_ID_2",
            "Credit/Debit card": "ID_PAY_SYSTEM_ID_50", 
            "PayPal": "ID_PAY_SYSTEM_ID_5"
        }

        # Randomly select any payment option
        selected_option_name = random.choice(list(payment_options.keys()))
        selected_option_id = payment_options[selected_option_name]
        
        print(f"Selected payment option: {selected_option_name} (ID: {selected_option_id})")

        # Only interact with the UI if it's not the default option
        if selected_option_name != "Bank transfer":
            # Find and click the payment option using its ID
            try:
                # Find and click the label of the payment option
                payment_label = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"label[for='{selected_option_id}']"))
                )
                print("Found payment label, attempting to click...")

                # Scroll to the label
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", payment_label)
                time.sleep(0.5)

                # Click the label
                payment_label.click()
                time.sleep(1)

                #Edit this piece
                """
                # Verify the option was selected by checking the input
                payment_input = driver.find_element(By.ID, selected_option_id)
                if payment_input.is_selected():
                    clean_option_name = selected_option_name.lower().replace(' ', '_').replace('\\', '_')
                    take_screenshot(f"selected_{clean_option_name}")
                    print(f"Successfully selected {selected_option_name} payment option")
                    return True, selected_option_name

                else:
                    print("Label click didn't change selection state")
                    # Fallback to JavaScript click if needed
                    driver.execute_script("arguments[0].click();", payment_input)
                    time.sleep(1)
                    if payment_input.is_selected():
                        print("Successfully selected using JavaScript fallback")
                        return True, selected_option_name
                    return False, selected_option_name"""

            except Exception as e:
                    print(f"Failed to select payment option {selected_option_name}: {str(e)}")
                    return False, selected_option_name
        else:
                print("Using default payment option (Bank transfer), no action needed")
                return True, selected_option_name

    except Exception as e:
            print(f"Error in payment selection process: {str(e)}")
            take_screenshot("payment_option_error")
            return False, "Error"



def fill_order_form():
    try:
        ship_to = choose_address() #is a dictionary
        country_name = ship_to['country']
        print(f"Chosen address in: {str(ship_to['city'])}")
        
        # Wait for the form to be present
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.ID, "EMAIL"))
        )
        print("Form found, starting to fill fields...")
        
        # Contact information
        print("Filling contact information...")
        
        # Email field
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "EMAIL"))
            )
            email_field.clear()
            email_field.send_keys(user_email)
            print("Email field filled")
        except Exception as e:
            print(f"✗ Error with email field: {str(e)}")
            take_screenshot("email_field_error")
            return False
        
        # Phone field
        try:
            # Different selector - no ID
            phone_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.NAME, "ORDER_PROP_88"))
            )
            phone_field.clear()
            phone_field.send_keys(test_phone)
            print("Phone field filled")
            
        except Exception as e:
            print(f"✗ Error with phone field: {str(e)}")
            take_screenshot("phone_field_error")
            return False
        
        # Name field
        try:
            name_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "FIO_SHIP"))
            )
            name_field.clear()
            name_field.send_keys("Alena Auto Test")
            print("Name field filled")

        except Exception as e:
            print(f"✗ Error with name field: {str(e)}")
            take_screenshot("name_field_error")
            return False  
               
        # Shipping address
        print("Filling shipping address...")

        # Select country in dropdown menu using Select object
        try:
            print(f"Selecting country: {country_name}")

            # Find the actual select element (it's visible and interactable!)
            country_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "COUNTRY_SHIPPING"))
            )
    
            # Create Select object
            select = Select(country_select)
    
            # Try to select by visible text
            select.select_by_visible_text(country_name)
            print(f"{country_name} is selected")
    
            time.sleep(1)
    
        except Exception as e:
            print(f"✗ Error with country field: {e}")
            traceback.print_exc()
            take_screenshot("country_field_error")
            return False
                    
        # City field 
        try:
            # Wait for the city field to be interactable
            city_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "CITY_SHIP"))
            )
            
            # Scroll to the element to ensure it's in view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", city_field)
            time.sleep(0.5)
            
            # Click on the field to ensure focus
            city_field.click()
            time.sleep(0.5)
            
            # Clear and fill the field
            city_field.clear()
            city_field.send_keys(ship_to['city'])
            print("City field filled")
            
            # Press Tab to move to next field (this might help with form validation)
            city_field.send_keys(Keys.TAB)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error with city field: {str(e)}")
            take_screenshot("city_field_error")
            return False
        
        # Address field
        try:
            address_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ADDRESS_SHIP"))
            )
            
            # Click to ensure focus
            address_field.click()
            time.sleep(0.5)
            
            address_field.clear()
            address_field.send_keys(ship_to['address'])
            print("Address field filled")
            
            # Press Tab to move to next field
            address_field.send_keys(Keys.TAB)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error with address field: {str(e)}")
            take_screenshot("address_field_error")
            return False
        
        # Postal code field
        try:
            postal_code_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ZIP_SHIP"))
            )
            
            # Click to ensure focus
            postal_code_field.click()
            time.sleep(0.5)
            
            postal_code_field.clear()
            postal_code_field.send_keys(ship_to['postal_code'])
            print("Postal code field filled")
            
        except Exception as e:
            print(f"✗ Error with postal code field: {str(e)}")
            take_screenshot("postal_code_field_error")
            return False
        
        # Billing address is the same as shipping (default tick remains)
        print("Billing address remains same as shipping (default)")

        # Order comment (2 lines)
        try:
            comment_field = driver.find_element(By.ID, "ORDER_DESCRIPTION")
            driver.execute_script('arguments[0].value = "Alena Auto Test\\nThis order was made by Alyona\'s helpful minions";', comment_field)
            print("Comment field filled")
        
        except Exception as e:
            print(f"✗ Error with comment field: {str(e)}")
            take_screenshot("comment_field_error")
        
        # Check delivery options
        print("Checking delivery options...")
        try:
            # Look for the specific courier delivery option
            courier_option = driver.find_element(By.CSS_SELECTOR, "label[for='ID_SHIPPING_METHOD_ID_23']")

            if courier_option:
                print("Found a courier delivery option as expected (Courier delivery)")
            else:
                print("✗ Could not find the Courier delivery option")

        except Exception as e:
            print(f"✗ Could not check delivery options: {str(e)}")
        
        print("✓ Order form filled successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error filling order form: {str(e)}")
        # Add traceback to see where it's failing
        traceback.print_exc()
        take_screenshot("order_form_error")
        return False



