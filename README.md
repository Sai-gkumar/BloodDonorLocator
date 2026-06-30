# 🔴 BloodLink - Real-Time Geolocation Blood Donor Locator

BloodLink is a real-time, map-based web application inspired by ride-sharing networks like Uber and Ola. It connects patient seekers with nearby, eligible blood donors dynamically. Built using **Flask**, **SQLite3**, and **Leafmap**, the application calculates real-time distances up to 1,000 KM using the Haversine formula and traces route overlays natively inside the dashboard interface.

---

## 🚀 Key Features

* **Live Interactive Map (Uber/Ola Style):** Features an address autocomplete search bar to look up target locations globally, accompanied by interactive donor pins.
* **Dynamic Radius & Blood Group Filters:** Narrow down matches by specific blood groups with a range slider stretching from 10 KM up to 1,000 KM.
* **On-Map Driving Routes:** Integrates Leaflet Routing Machine to plot a direct driving path overlay from the search center to a selected donor's spot.
* **Gamified Donor Milestones (Badges):** Automatically awards rank badges based on contribution counts (`👑 Life Saver Elite`, `🛡️ Blood Champion`, `🩸 First Responder`, `🌱 New Donor`).
* **Interactive Registration Map:** Donors can input coordinates using a text address search box, clicking anywhere on the map grid, or using HTML5 live location auto-detection.
* **Self-Service User Profile:** Logged-in donors can alter contact records, modify login security credentials, or turn off availability status toggles.
* **Administrative Dashboard:** Full access control to manage accounts, delete users, flip availability states, and simulate system-wide emergency alerts.

---

## 📁 Project Directory Structure

```text
BloodDonorLocator/
│
├── database.db             # Generated automatically on initialization
├── init_db.py              # Script to build tables and seed mock data
├── app.py                  # Main Flask backend application engine
├── requirements.txt        # Backend dependencies manifest
│
├── static/
│   ├── css/
│   │   └── style.css       # Layout styles and badge color definitions
│   └── generated_maps/
│       └── live_map.html   # Isolated UTF-8 compliant Leafmap engine frame
│
└── templates/
    ├── base.html           # Master layout shell (loads Leaflet core assets)
    ├── index.html          # Main map search panel UI
    ├── register_donor.html # Registration template with address search options
    ├── login.html          # User authentication page
    ├── dashboard.html      # Self-service donor credentials panel
    ├── admin.html          # Administrative console panel
    └── donor_profile.html  # Full-page individual profile view layout

```

---

## 🛠️ Installation & Setup Guide

Follow these steps to launch the application on your local machine:

### 1. Clone or Create the Project Directory

Set up your folder structure matching the directory schema detailed above and add the respective codebase configurations.

### 2. Install Project Dependencies

Open your terminal or command prompt, navigate to the project root directory, and execute:

```bash
pip install -r requirements.txt

```

### 3. Initialize the Database Schema

Run the database generator script to create the SQLite tables and seed them with administrative accounts and mock donors around the Visakhapatnam region:

```bash
python init_db.py

```

### 4. Boot Up the Application Server

Launch the Flask development engine server instance:

```bash
python app.py

```

### 5. Access the Web Application

Open your web browser and navigate to:

```text
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

```

---

## 🔐 Credentials for Testing

Use the following pre-configured credentials to evaluate the different profile layers:

### 🛠️ System Administrator Account

* **Email:** `admin@bloodlink.com`
* **Password:** `admin123`

### 🩸 Preloaded Mock Donors

You can log in as any of these seeded donors to view the **User Profile Panel**:

1. **Life Saver Elite (O+):** `ravi@gmail.com` (Password: `pass123`)
2. **Blood Champion (A+):** `kavya@gmail.com` (Password: `pass123`)
3. **First Responder (B+):** `deelip@gmail.com` (Password: `pass123`)

---

## 🛡️ Core Tech Stack & Libraries

* **Backend Framework:** Python Flask
* **Geospatial Visualization:** Leafmap (Folium/Leaflet engine)
* **Routing Services:** Leaflet Routing Machine
* **Geocoding/Search API:** OpenStreetMap Nominatim Engine
* **Database Engine:** SQLite3