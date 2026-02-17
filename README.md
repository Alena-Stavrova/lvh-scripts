# lvh-scripts
Stack: Python, Selenium

These scripts automate order placement that is a part of our regression testing/system health check. They imitate real user's behavior:
* go to the main page
* search for a particular item (chosen randomly from a list of SKUs, the list contains different price groups)
* add the item to cart
* fill order form
* select payment and/or delivery options randomly (whichever are available on a particular website). Sometimes includes interactive 3rd party elements (dropdowns, maps etc.)
* place an order
* print a helpful summary in the end (e.g. order number, item's price, cost of delivery etc.)

Currently there is only the US <img width="16" height="11" alt="image" src="https://github.com/user-attachments/assets/9eb448d4-69e2-4597-953a-573c44ff8f9c" /> script as I'd like to polish it real well before adapting it to other scripts. In the future, I'll add scripts for other countries (we currently have 10).

