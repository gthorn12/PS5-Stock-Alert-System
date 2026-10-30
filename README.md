# PS5 Pro Stock Monitor

A Python-based inventory monitoring application designed to check PlayStation 5 Pro availability across multiple Target locations and send push notifications when stock becomes available.

## Features

- **Multi-store inventory monitoring:** Checks availability across seven Target locations in Arizona.
- **Dynamic scheduling:** Automatically calculates the interval between inventory checks.
- **Push notifications:** Uses ntfy to deliver inventory alerts to a mobile device.
- **API integration:** Retrieves and processes inventory information from an external API.
- **Inventory filtering:** Identifies locations with available inventory and filters out unavailable products.
- **Console logging:** Displays inventory status, quantities, remaining API credits, and the next scheduled check.

## Technologies Used

- Python
- REST APIs
- Requests
- python-dotenv
- ntfy

## How It Works

The application periodically requests inventory data for a selected product across multiple retail locations.

Each response is parsed to determine availability and inventory quantity. When an eligible location reports available stock, the application can send a push notification.

The application uses dynamic scheduling to manage the frequency of requests while monitoring API usage.

## Configuration

The application requires an API key and notification configuration. Sensitive credentials are stored in environment variables rather than hardcoded into the source code.

## Motivation

I developed this application to help my brother find a PlayStation 5 Pro without having to manually check inventory at multiple stores throughout the day.

The project became an opportunity to explore API integration, automated monitoring, scheduling, and mobile notifications.

## Project Status

The application is operational and has successfully completed extended monitoring sessions. Live detection of an actual restock has not yet been verified.