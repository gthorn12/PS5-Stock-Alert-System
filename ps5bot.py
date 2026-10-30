
"""
This script is an automated ps5 availability bot.

Author: Grady Horn
Date: 2026-10-27

The script functions by using Scavio to send an
API request to check the availability of the 
PS5 Pro products at Target stores. Upon finding
the desired item, it sends a notification via ntfy.
"""
import os
import json
import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo
# from playwright.sync_api import sync_playwright
from pathlib import Path
from scavio import ScavioClient
from dotenv import load_dotenv

load_dotenv()

MY_KEY = os.environ["API_KEY"]
TOPIC = os.environ["NTFY_TOPIC"]

URL_0 = "https://www.target.com/p/playstation-5-pro-console/-/A-93620188"

'''
BRAVE_PATH = r"C:\Users\grady\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
PROFILE_PATH = r"C:\Users\grady\Documents\ps5BotProfile"

print("Brave Exists:", Path(BRAVE_PATH).is_file())
print("Profile Path Exists:", Path(PROFILE_PATH).is_dir())

with open("targetResponse.json", "r", encoding="utf-8") as file:
        target_response = json.load(file)
'''

PS5_PRO_TCIN = "93620188"
PS5_DIGITAL_TCIN = "94961316"
PRODUCT_TCIN = PS5_PRO_TCIN
TARGET_ZIP = os.getenv("TARGET_ZIP", "85140")


def loadLocalStorage():
    try:
        with open("localStorage.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def saveLocalStorage(data):
    with open("localStorage.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def sendScavioRequest():
    successfulHits = []
    client = ScavioClient(api_key=MY_KEY)
    try:
        stock = client.target.availability(PRODUCT_TCIN, zip=TARGET_ZIP)
    except Exception as e:
        print("Error fetching stock availability:", e)
        return None

    try:
        stores = stock["data"]["stores"]
    except KeyError:
        print("Error: Scavio did not return a valid stores list.")
        return None
 
    for store in stores:
        if store["in_store"] != "out_of_stock" and store["quantity"] > 0:
            if PRODUCT_TCIN == PS5_DIGITAL_TCIN:
                productName = "PS5 Digital"
            elif PRODUCT_TCIN == PS5_PRO_TCIN:
                productName = "PS5 Pro"
            successfulHits.append(
                f"{store['name']} has {store['quantity']} {productName}"
                f"{'' if store['quantity'] == 1 else 's'} available in-store!"
            )

        print(
            f"{store['name']}: "
            f"{store['in_store']} "
            f"(Quantity: {store['quantity']})"
        )

    return successfulHits

def getScavioCredits():
    client = ScavioClient(api_key=MY_KEY)

    try:
        usage = client.get_usage()
        remainingCredits = usage["credit_balance"]
    except Exception as e:
        print("Error fetching Scavio credits:", e)
        return None

    return remainingCredits

# def logResponse(response):
#     if "cdui_orchestrations" in response.url:
#         print("Status:", response.status)
#         print("Content type:", response.headers.get("content-type"))

#         if response.status == 435:
#             print("Target rejected or challenged this request.")

# def openBrowser():
#     with sync_playwright() as p:
#         context = p.chromium.launch_persistent_context(
#             user_data_dir=PROFILE_PATH,  
#             executable_path=BRAVE_PATH,
#             headless=False
#             )

#         page = context.new_page()
#         page.on("response", logResponse)
#         page.goto(URL_0)

#         print("Current URL:", page.url)
#         print("Page title:", page.title())

#         input("Press Enter to close the browser.")

# def checkPs5Availability(target_response):
    
#     try:
#         modules = target_response["modules"]
#         data = None
#         totalResponse = []
#         for module in modules:
#             if module["module_type"] == "ProductDetailWebDatasourceFulfillmentAndVariations":
#                 data = module["module_data"]["data"]["product"]["fulfillment"]
#                 print("Fulfillment data:", data)
#                 break

#         if data is not None:
#             stores = data["store_options"]
#             for store in stores:
#                 pickupStatus = store["order_pickup"]["availability_status"]
#                 inStoreStatus = store["in_store_only"]["availability_status"]
#                 storeName = store["store"]["location_name"]
#                 """
#                 print("Pickup Status:", pickupStatus)
#                 print("In-Store Status:", inStoreStatus)
#                 print("Store Name:", storeName)
#                 """
#                 if pickupStatus != "OUT_OF_STOCK":
#                     """print(f"{storeName} has a PS5 Pro available for online pickup!")"""
#                     totalResponse.append(f"{storeName} has a PS5 Pro available for online pickup!")
#                 if inStoreStatus != "OUT_OF_STOCK":
#                     """print(f"{storeName} has a PS5 Pro available in-store only!")"""
#                     totalResponse.append(f"{storeName} has a PS5 Pro available in-store only!")
#             if not totalResponse:
#                 totalResponse.append("No stores have a PS5 Pro available.")
#         else:
#             print("Fulfillment data not found.")
                
#     except KeyError as e:
#         print("Key error occurred:", e)

#     return totalResponse

def sendNtfyAlert(message):
    try:
        response = requests.post(
            f"https://ntfy.sh/{TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": "PS5 Pro Stock Alert",
                "Priority": "high",
                "Tags": "video_game,tada",
                "Click": "https://www.target.com/p/-/A-93620188"
            },
            timeout=10
        )

        print(f"HTTP Status: {response.status_code}")
        print(f"Server Response: {response.text}")
        
        response.raise_for_status()
        
        print("Notification accepted by ntfy!")
        return True

    except requests.RequestException as e:
        print("Error sending ntfy alert:", e)
        return False

def calculateInterval():
    currTime = datetime.now(ZoneInfo("America/Phoenix"))
    hr = currTime.hour
    min = currTime.minute
    sec = currTime.second
    minAdjust = 0

    if hr >= 0 and hr < 5:
        intervalMins = 30
        minAdjust = intervalMins - (min % intervalMins)
        interval = minAdjust * 60 - sec

    elif hr >= 5 and hr < 10:
        intervalMins = 2
        minAdjust = intervalMins - (min % intervalMins)
        interval = minAdjust * 60 - sec

    elif hr >= 10 and hr < 22:
        intervalMins = 5
        minAdjust = intervalMins - (min % intervalMins)
        interval = minAdjust * 60 - sec

    else:
        intervalMins = 15
        minAdjust = intervalMins - (min % intervalMins)
        interval = minAdjust * 60 - sec

    print(f"Arizona time: {currTime:%I:%M:%S %p} | Next check in {interval} seconds.")
    return interval

"""
Test code for checking PS5 availability 
and opening the browser.


results = checkPs5Availability(target_response)
for result in results:
    print(result)

openBrowser()
"""

if __name__ == "__main__":
    localStorage = loadLocalStorage()
    remainingCredits = getScavioCredits()
    firstAttempt = True

    if localStorage.get("zip") != TARGET_ZIP:
        previousHits = []
    else:
        previousHits = localStorage.get("previousHits", [])

    while True:
        if remainingCredits is None:
            print("Failed to fetch remaining credits. Stopping script.")
            break

        if remainingCredits <= 0:
            print("No remaining credits. Stopping script.")
            break

        successfulHits = sendScavioRequest()
        remainingCredits = getScavioCredits()

        if remainingCredits is None:
            print("Failed to fetch remaining credits. Stopping script.")
            break

        print(f"Inventory check completed. Results: {successfulHits}")
        print(f"Credits remaining: {remainingCredits}")

        if firstAttempt and successfulHits is not None:
            sendNtfyAlert("PS5 Pro Stock Alert System is live! First inventory check successful!")
            firstAttempt = False

        if successfulHits is not None:
            if successfulHits != previousHits:
                if not successfulHits:
                    message = "PS5 Pros are now unavailable."
                else:
                    message = "\n".join(successfulHits)

                if sendNtfyAlert(message):
                    previousHits = successfulHits

        saveLocalStorage({
            "zip": TARGET_ZIP,
            "previousHits": previousHits,
            "remainingCredits": remainingCredits
        })

        time.sleep(calculateInterval())  # Wait for the calculated interval before the next iteration




   
