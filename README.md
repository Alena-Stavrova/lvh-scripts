# lvh-scripts
Stack: Python, Selenium

These scripts automate order placement that is a part of our regression testing/system health check. They imitate a real user's behavior:
* go to the main page
* search for a particular item (chosen randomly from a list of SKUs, the list contains different price groups)
* add the item to cart
* fill order form
* select payment and/or delivery options randomly (whichever are available on a particular website). Sometimes includes interactive 3rd party elements (dropdowns, maps etc.)
* place an order
* print a helpful summary in the end (e.g. order number, item's price, cost of delivery etc.)

Scripts done:  DE <img width="16" height="11" alt="image" src="https://github.com/user-attachments/assets/9eb448d4-69e2-4597-953a-573c44ff8f9c"> EU <img width="16" height="11" alt="image" src="https://github.com/user-attachments/assets/787a3df3-27a0-4cb7-806d-3aae9e26ffe4" />  IT <img width="16" height="11" alt="image" src="https://raw.githubusercontent.com/stevenrskelton/flag-icon/master/png/16/country-4x3/it.png">  US <img width="16" height="11" alt="image" src="https://github.com/user-attachments/assets/9eb448d4-69e2-4597-953a-573c44ff8f9c"/> (4 / 10)

For each country*, there will be 2 scripts:
* <ins>random</ins>: choose payment and/or delivery option randomly; used for daily smoke tests where we typically test 1 random flow
* <ins>choice</ins>: choose payment and/or delivery option that the user selects; can test any flow within possible payment/delivery combinations; used for montly system health check where we typically test all flows or all flows with 3rd-party systems

*Except US because they only have 1 flow available

UPD March 18 '26: Added a runner script so that several scripts can be run automatically one after another (just like ERM). The versions posted here are:

* V1 = current working version that doesn't work with the runner yet
* V2 = a version compatible with the runner
