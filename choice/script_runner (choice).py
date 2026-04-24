#import BG_random_V3 as bg
#import CZ_random_V3 as cz
import DE_choice_V3 as de
#import ES_random_V3 as es
#import EU_random_V3 as eu
import HU_choice_V3 as hu
import IT_choice_V3 as it
#import PL_random_V3 as pl
#import TR_random_V3 as tr
#import US_random_V3 as us

import random

script_modules = {
    #'BG': bg,
    #'CZ': cz,
    'DE': de,
    #'ES': es,
    #'EU': eu,
    'HU': hu,
    'IT': it,
    #'PL': pl,
    #'TR': tr,
    #'US': us
    }

print("Type countries and the number of orders like so: 'ES:1 DE:2'")
print("The example above will make 1 order on ES website and 2 orders on DE website")
scripts_string = input("Enter your choice: ")

scripts_to_run = {i.split(":")[0]: int(i.split(":")[1]) for i in scripts_string.split(" ")}

# Initialize test data
test_email = input("Enter email: ")
test_phone = "+79444444444"
second_email = None
script_count = 0

#{'DE':4, 'HU':2}

for k in scripts_to_run:
    module = script_modules[k]
    run_num = scripts_to_run[k]
    for j in range(run_num):        
        main_function = getattr(module, f"main_{k.lower()}")
    
        print(f"\n{'='*60}")
        print(f"Running {k} script with email: {test_email}")
        print(f"{'='*60}")
    
        main_function(test_email, test_phone)
        script_count += 1
        if script_count == 5:
            print(f"\n{'='*60}")
            test_email = input("Made 5 orders, please enter NEW email: ")
            print(f"\n{'='*60}")
            script_count = 0
