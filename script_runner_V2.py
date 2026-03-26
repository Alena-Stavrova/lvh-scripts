#import BG_random_V2 as bg
import CZ_random_V2 as cz
import DE_random_V2 as de
#import ES_random_V2 as es
import EU_random_V2 as eu
#import HU_random_V2 as hu
import IT_random_V2 as it
#import PL_random_V2 as pl
#import TR_random_V2 as tr
import US_random_V2 as us

import random
import time

script_modules = {
    #'BG': bg,
    'CZ': cz,
    'DE': de,
    #'ES': es,IT
    'EU': eu,
    #'HU': hu,
    'IT': it,
    #'PL': pl,
    #'TR': tr,
    'US': us
    }

def run_script(script_name, email, phone):
    """Run a single script and return True if order was placed successfully"""
    try:
        module = script_modules[script_name]
        main_function = getattr(module, f"main_{script_name.lower()}")
        
        print(f"\n{'='*60}")
        print(f"Running {script_name} script with email: {email}")
        print(f"{'='*60}")
        
        # Call the script and capture the result (if it returns order number)
        result = main_function(email, phone)
        
        # Check if order was placed successfully
        # Adjust this condition based on what your scripts return
        if result and result != "order wasn't placed":
            print(f"✓ {script_name} completed successfully")
            return True
        else:
            print(f"✗ {script_name} failed to place order")
            return False
        
    except Exception as e:
        print(f"✗ {script_name} crashed with error: {str(e)}")
        return False

scripts_string = input('Type countries space-separated, like "ES EU PL" or "8" to run ALL the scripts: ')
if scripts_string == "8":
    scripts_to_run = ['BG', 'CZ', 'DE', 'ES', 'EU', 'HU', 'IT', 'PL', 'TR', 'US']
else: 
    scripts_to_run = scripts_string.upper().split() # is a list

# Shuffles the list randomly to run scripts in diff order
random.shuffle(scripts_to_run)

# Initialize test data
test_email = input("Enter email: ")
test_phone = "+79444444444"
second_email = None

if len(scripts_to_run) > 5:
    second_email = input('More than 5 scripts, please type in additional email: ')

# First pass: run all scripts
failed_scripts = []
script_count = 0

for script in scripts_to_run:
    current_email = test_email if script_count < 5 else second_email

    success = run_script(script, test_email, test_phone)
    
    if not success:
        failed_scripts.append((script, test_email))
    
    script_count += 1
    time.sleep(2)  # Small pause between scripts to avoid overwhelming the server
    
# Second pass: retry failed scripts
if failed_scripts:
    print(f"\n{'='*60}")
    print(f"RETRYING {len(failed_scripts)} FAILED SCRIPTS")
    print(f"{'='*60}")
    
    retry_success = []
    for script, email in failed_scripts:
        print(f"\nRetrying {script}...")
        success = run_script(script, test_email, test_phone)
        if success:
            retry_success.append(script)
        time.sleep(2)

# Final summary
print(f"\n{'='*60}")
print("RUNNER SUMMARY")
print(f"{'='*60}")
print(f"Total scripts run: {len(scripts_to_run)}")
print(f"Success on first try: {len(scripts_to_run) - len(failed_scripts)}")
if failed_scripts:
    print(f"Failed on first try: {len(failed_scripts)}")
    print(f"  {', '.join([s[0] for s in failed_scripts])}")
    if retry_success:
        print(f"Recovered on retry: {len(retry_success)}")
        print(f"  {', '.join(retry_success)}")
    still_failed = [s for s in failed_scripts if s[0] not in retry_success]
    if still_failed:
        print(f"Still failed after retry: {len(still_failed)}")
        print(f"  {', '.join([s[0] for s in still_failed])}")
print(f"\n{'='*60}")
        
    
