import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOPIC = os.environ["NTFY_TOPIC"]

print("sending notification...")
print(f"Topic: {TOPIC}")

try:
    response = requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data="PS5 Pro notification test!".encode("utf-8"),
        headers={
            "Title": "PS5 Bot test",
            "Priority": "high",
            "Tags": "tada!"
        },
        timeout=10
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"Server Response: {response.text}")

    response.raise_for_status()

    print("Notification accepted by ntfy!")

except requests.exceptions.RequestException as e:
    print(f"ERROR: {e}")