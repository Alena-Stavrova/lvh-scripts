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

Scripts done:  CZ <img width="16" height="11" alt="CZ flag" src="https://cz.levenhuk.com/upload/uf/aae/3xkmguzh9wbv2rf1tihnbrwqe2g7opub/CZ.svg"> | DE <img width="16" height="11" alt="DE flag" src="https://de.levenhuk.com/upload/uf/c3d/0g1sijegx0japf8h3xrmfwe38yhzncs4/DE.svg"> | ES <img width="16" height="11" alt="ES flag" src="https://es.levenhuk.com/upload/uf/240/7xfauisyvrj1lvq4xo6ez8edulm4jx1b/ES.svg" /> | EU <img width="16" height="11" alt="EU flag" src="https://eu.levenhuk.com/upload/uf/3c6/mjgpqapw7zairhbqam8ti91z8koanis2/EU.svg" /> | IT <img width="16" height="11" alt="IT flag" src="https://it.levenhuk.com/upload/uf/902/r191twfwccz3c5yrbdkt32r19fi4trzz/IT.svg"> | PL <img width="16" height="11" alt="PL flag" src="https://pl.levenhuk.com/upload/uf/004/b9fnsrp8csujk4mh0bnf0a3ykokyzm7d/PL.svg"> | US <img width="16" height="11" alt="US flag" src="https://levenhuk.com/upload/uf/414/s7dkq0gx4i2sba9e0zquy5doxzy1qhy3/USA.svg"/> (7 / 10)

For each country*, there will be 2 scripts:
* <ins>random</ins>: choose payment and/or delivery option randomly; used for daily smoke tests where we typically test 1 random flow
* <ins>choice</ins>: choose payment and/or delivery option that the user selects; can test any flow within possible payment/delivery combinations; used for montly system health check where we typically test all flows or all flows with 3rd-party systems

*Except US because they only have 1 flow available

UPD March 18 '26: Added a runner script so that several scripts can be run automatically one after another (just like ERM). The versions posted here are:

* V1 = current working version that doesn't work with the runner yet
* V2 = a version compatible with the runner
