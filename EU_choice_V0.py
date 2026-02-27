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

# Initialize driver with None (to be changed later)
driver = None
wait = None
website_main = "https://eu.levenhuk.com/"
test_phone = "+79444444444"

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
    
    local_driver = webdriver.Chrome(options=options)
    
    # Longer timeout for initial load
    local_driver.set_page_load_timeout(60)
    
    return local_driver

def take_screenshot(name):
    global driver
    # Create screenshot folder, name screenshot images
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    filename = f"screenshots/{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"(Screenshot saved as: {filename})")
    return filename

# Step counter class to count step number automatically
class StepCounter:
    def __init__(self):
        self.step = 1
    
    def print_step(self, message):
        print(f"\n--- Step {self.step}: {message} ---")
        self.step += 1

# List of SKUS and price classes
sku_lists = {
    0: [83836, 83820, 84547, 84545, 83089],  # Under 70 EU
    1: [84558, 84638, 84087, 83842, 85574]   # 70+ EU
}
items_unavailable = []

# Choose sku for the chosen payment option
def choose_sku(price_class):
    # Get the correct list from the dictionary
    skus_list = sku_lists[price_class]  
    print(f"Using SKU list for class {price_class}")
    
    available_skus = [str(sku) for sku in skus_list if str(sku) not in items_unavailable]
    #print(f"Available SKUs: {available_skus}")
    
    if not available_skus:
        return None
    
    return random.choice(available_skus)

# Key in the bigger dictionary = user input numbers
payment_options = {
    1: {'name_en': 'Bank transfer',
     'id': 'ID_PAY_SYSTEM_ID_2'},

    2: {'name_en': 'Credit/Debit Card',
     'id': 'ID_PAY_SYSTEM_ID_50'},
    
    3: {'name_en': 'PayPal',
     'id': 'ID_PAY_SYSTEM_ID_5'},

    4: {'name_en': 'TBD',
     'id': None} # TBD method doesn't have a button
}

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
        'country': 'Ireland',
        'city': 'Galway', 
        'address': '105 Forster Ct',
        'postal_code': 'H91 D95P'
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

        close_cookie_popup()
        
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
        card_sku = card_sku_elem.text[-5:]
        print(f"SKU on the product card is: {card_sku}")
        
        # Scroll to the element to take screenshot
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_sku_elem)
        time.sleep(2)
        take_screenshot("search_results")

        if sku == card_sku:        
            print("Search completed successfully")
            return True
        else:
            print(f"✗ First found item doesn't match the search: looked for {sku}, firs item is {card_sku}")
            return False
        
    except Exception as e:
        print(f"✗ Search failed: {str(e)}")
        take_screenshot("search_error")
        return False

def is_item_available(sku):
    # Is only applied when sku != None
    try:
        search_for_sku(sku)
        price_text = driver.find_element(By.CLASS_NAME, "catalog-card__price").text.lower()
        unavailable_indicators = ["out of stock", "discontinued", "coming soon"]
        if any(indicator in price_text for indicator in unavailable_indicators):
            return False, price_text
        else:
            cart_button = driver.find_element(By.CLASS_NAME, "catalog-card__cart")
            if cart_button.is_displayed():
                return True, "available"
            else:
                return False, "unclear"

    except Exception as e:
        return False, str(e)

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

def click_payment_option(option_id):
    # Click button if not TBD and not default option
    try:
        payment_label = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"label[for='{option_id}']"))
        )
        payment_label.click()
        time.sleep(1)
        return True
        
    except Exception as e:
        print(f"Can't find or click the payment option: {str(e)}")
        take_screenshot("payment_option_error")
        return False

def fill_order_form():
    global delivery_option_summary, payment_option_summary # We'll modify the global variable
    try:
        ship_to = choose_address() #is a dictionary
        country_name = ship_to['country']
        print(f"Chosen address in: {str(ship_to['country'])}, {str(ship_to['city'])}")
        
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
            #courier_option = driver.find_element(By.CSS_SELECTOR, f"label[for='{exp_delivery_id}']")
            courier_option = driver.find_element(By.CSS_SELECTOR, default_dselector) 

            if courier_option:
                print(f"Found 1 delivery option as expected ({default_dbutton})")
                delivery_option_summary = default_dbutton
                # Scroll to the delivery section to take screenshot
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", courier_option)
                time.sleep(2)
                take_screenshot("delivery_section")
                
            else:
                print(f"✗ Could not find the {exp_delivery} option")

        except Exception as e:
            print(f"✗ Could not check delivery options: {str(e)}")

        # Click button for items 70+ EU unless default (Bank transfer)
        if price_class == 1 and popt_name != "Bank transfer":
            # Select payment option, if price is 70+ EU
            option_click_success = click_payment_option(popt_id)
            time.sleep(2)

            if not option_click_success:
                print("✗ Payment selection failed")
                print("WARNING: payment option {payment_option} didn't work as expected - please check manually. Quitting the program.")
                driver.quit()
                sys.exit()
            else:
                payment_option_summary = popt_name
                
        elif price_class == 1: # Default option, no need to click
            print("Using default payment option for itmes 70+€")
            payment_option_summary = default_pbutton

        else:
            # Items under 70 EU, no button
            print("Using default payment option for itmes under 70€")
            payment_option_summary = no_pbutton

        print("✓ Order form filled successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error filling order form: {str(e)}")
        # Add traceback to see where it's failing
        traceback.print_exc()
        take_screenshot("order_form_error")
        return False

def place_order():
    # Finalize the order by clicking the checkout button on the order form
    try:
        print("Placing final order...")
        
        take_screenshot("before_final_order")
        
        # Find and click the checkout button
        checkout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        print(f"Found checkout button")
        
        # Scroll to button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_button)
        time.sleep(1)
        checkout_button.click()
        return True
        
    except Exception as e:
        print(f"✗ Error in final order submission: {str(e)}")
        take_screenshot("final_order_error")
        return False
    
def get_order_number():
    # Get the order number from the URL of the confirmation page
    # URL is like: https://levenhuk.com/order/?ORDER_ID=T-B2C-US-41574
    try:
        current_url = driver.current_url
        if "ORDER_ID=" in current_url:
            # Slicing different number of characters for test ("T-") and regular orders
            # Will need to edit if > 99,999 orders
            if "T-" in current_url:
                order_num = current_url[-14:]
            else:
                order_num = current_url[-12:]
            print(f"✓ Order confirmed! Order number: {order_num}")
            return order_num
                
        else:
            print(f"✗ Order number is not in current url")
            return False
        
    except Exception as e:
        print(f"✗ Error in final order submission: {str(e)}")
        take_screenshot("final_order_error")
        return False
    
# Main execution
if __name__ == "__main__":

    print("Running EU script")
    print("---------------LOGS FOR NERDS---------------")

    # Get al the user input first (no browser yet)
    user_email = input("Enter email: ")   

    # Get payment option from user      
    while True:
        try:
            print("\nPayment options:")
            print("1 = Bank transfer (70+€ items)")
            print("2 = Credit/Debit Card (70+€ items)")
            print("3 = PayPal (70+€ items)")
            print("4 = TBD (items under 70€)")
            
            selected_payment = int(input("Enter your option (1-4): "))
            if selected_payment in [1, 2, 3, 4]:
                break
            else:
                print("✗ Please enter a number between 1 and 4.")

        except ValueError:
            print("✗ Please enter a valid number.")

    # Determine price class based on payment
    price_class = 1 if selected_payment in [1, 2, 3] else 0

    # Get payment option details
    popt_name = payment_options[selected_payment]['name_en']
    popt_id = payment_options[selected_payment]['id']
    print(f"\nSelected: {popt_name} (Price class: {'70+€' if price_class == 1 else 'under 70€'})")
        
    print("\nLaunching browser...")
    driver = create_optimized_driver()
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    # Initialize default options 
    default_pbutton = "Bank transfer"
    no_pbutton = "TBD"
    default_dbutton = "Courier delivery"
    default_dselector = 'label[for="ID_SHIPPING_METHOD_ID_4"]'

    # Initialize all variables for the summary at the end
    delivery_option_summary = None
    payment_option_summary = None
    basket_price = None
    order_price = None
    order_result = None
    # Add free shipping check later
       
    # Initialize step counter
    step_counter = StepCounter()

    try:
        while True:
            # Only choose the skus that are NOT in unavailable_items
            my_sku = choose_sku(price_class)
            if my_sku != None:
                print(f"Chosen SKU: {str(my_sku)}")

                step_counter.print_step("Searching for SKU, checking its availability")
                # Avaialability check already includes search_for_sku
                available, status = is_item_available(my_sku)
    
                if available:
                    print(f"✓ SKU {my_sku} is available")
                    break
                
                # If item is NOT available:
                else:
                    if len(items_unavailable) < len(sku_lists[price_class]): 
                        print(f"✗ SKU {my_sku} not available: {status}")
                        items_unavailable.append(str(my_sku))
                        time.sleep(1)  # Small delay before retry

            # If choose_sku() returns None, meaning all items are unavailable
            else:
                print("✗ All items are UNAVAILABLE")
                print("Closing the browser")
                driver.quit()
                sys.exit()
        
        step_counter.print_step("Getting offer ID")
        offer_id = get_offer_id(my_sku)

        if offer_id:
            step_counter.print_step("Adding to cart via API")
                
            if add_to_cart_via_api(offer_id, 1):
                print("Refreshing page to synchronize UI")
                driver.refresh()
                time.sleep(1)
                step_counter.print_step("Navigating to cart")

                if navigate_to_cart_directly():
                    step_counter.print_step("Checking cart contents")
                    if check_cart_contents(my_sku):
                        step_counter.print_step("Getting cart total price")
                        basket_price = get_total_price()

                        if basket_price is not None:
                            print(f"Cart total price: {basket_price}")
                                
                            step_counter.print_step("Proceeding to checkout")
                            take_screenshot("basket_before_checkout")
                                
                            if proceed_to_checkout():
                                step_counter.print_step("Getting order page total price")
                                order_price = get_total_price()

                                if order_price is not None:
                                    print(f"Order page total price: {order_price}")
                                        
                                    # Compare prices
                                    if abs(basket_price - order_price) < 0.01:  # Account for floating point precision
                                        print("✓ SUCCESS: Prices match between cart and order pages!")
                                        take_screenshot("order_with_price")

                                        fill_form_success = fill_order_form()
                                        if fill_form_success:
                                            step_counter.print_step("Placing order")
                                            order_result = place_order()

                                            if order_result:
                                                print("✓ Order successfully placed!")
                                                time.sleep(3)
                                                step_counter.print_step("Getting the order number")
                                                test_order_num = get_order_number()

                                            else:
                                                print("✗ Failed to place order")                                                

                                        else:
                                            print("✗ Failed to fill order form") 
                                            
                                    else:
                                        print(f"✗ WARNING: Prices don't match! Cart: {basket_price}, Order: {order_price}")
                                                                                       
                                else:
                                    print("✗ Could not extract price from order page")
                            else:
                                print("\n✗ Failed to proceed to checkout")
                        else:
                            print("\n✗ Could not extract price from cart page")
                    else:
                        print("\n✗ Item was added but not found in cart")
                else:
                    print("\n✗ Failed to navigate to cart")
            else:
                print("\n✗ Failed to add item to cart via API")
        else:
            print("\n✗ Could not find offer ID for the product")
        
        print("\nProcess completed. Browser will close in 10 seconds.")

        print("----------ORDER INFO----------")
        if order_result:
            print(f"Order number: {test_order_num}") # Will return False in case of error
        else:
            print("Order number: order wasn't placed")
        print(f"Chosen SKU: {str(my_sku)}")
        print(f"Item price: {order_price if order_price else 'N/A'}€")
        print(f"Delivery option: {delivery_option_summary}")
        print(f"Payment option: {payment_option_summary}")
            
        # Price match check
        if basket_price and order_price:
            if abs(basket_price - order_price) < 0.01:
                print("Cart and order prices match: ✓ Yes")
            else:
                print(f"Cart and order prices match: ✗ No (Cart: {basket_price}, Order: {order_price})")
        else:
            print("Cart and order prices match: N/A (missing price data)")
        
        print("----------END----------")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n✗ Script failed with error: {str(e)}")
        take_screenshot("main_script_error")          
   
    finally:
        time.sleep(5)
        driver.quit()



