import requests
BASE_URL = "http://10.6.131.127:5000/"

## GET EXAMPLES FOR RETRIEVING DATA ##

# This will return a dictionary containing the state of all the relay groups.
requests.post(BASE_URL + "7/auto=on")
requests.post(BASE_URL + "status-dict")