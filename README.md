# Weather Automation ELT Pipeline

A Python-based pipeline for **Extracting**, **Loading**, and **Transforming** (ELT) weather data from various sources into a unified, ready-to-analyze format. This project was designed to automate fetching weather data, storing it, then transforming it for consistency, and optionally loading it back into storage such as CSV files on AWS S3 buckets (e.g., S3).

## Table of Contents

1. [Overview](#overview)  
2. [Project Structure](#project-structure)  
3. [Getting Started](#getting-started)  
4. [Usage](#usage)  
5. [Configuration](#configuration)  
6. [Docker Instructions](#docker-instructions)  
7. [Planned Features](#planned-features)  
8. [Contributing](#contributing)  
9. [License](#license)

---

## Overview

- **Fetch** weather data from public APIs.
- **Load** the data into Json files upload to an AWS S3 bucket (configurable via environment variables).
- **Transform** the collected JSON data into a normalized format and converted to CSV format and sent back to S3 for storage. 


Core scripts:
- **`fetch_weather_data.py`** / **`fetch_data.py`**: Pull weather data from various APIs.  
- **`transform_weather_data.py`**: Convert raw data to a more usable form.  
- **`App.py` / `main.py`**: Possible entry points or orchestrators of the pipeline.  
- **`data_retrived.py`**: Function for automatic retrival of data from the API using Docker.

---

## Project Structure

```
test_weather/
├─ .venv/                   # (Optional) Local virtual environment
├─ config.env               # Environment variables (ignored by Git)
├─ data_retrived.py         # Data retrieval logic
├─ docker-compose.yml       # Orchestrates multiple Docker containers 
├─ Dockerfile.fetch         # Dockerfile for the fetch service
├─ Dockerfile.transform     # Dockerfile for the transform service
├─ fetch_weather_data.py    # Another variant for fetching data
├─ App.py                   # Streamlit application for realtime data visualization
├─ requirements.txt         # Python dependencies
├─ transform_weather_data.py # Python file for transforming raw data
└─ README.md                # <--- You are here!
```

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/weather-automation-elt.git
   cd weather-automation-elt
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Mac/Linux
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Set up your environment variables** in `config.env` (or a `.env` file), for example:
   ```ini
   AWS_ACCESS_KEY=YOUR_ACCESS_KEY
   AWS_SECRET_KEY=YOUR_SECRET_KEY
   S3_BUCKET=YOUR_BUCKET_NAME
   WEATHER_API_KEY=YOUR_WEATHER_API_KEY
   ```
2. **Run the data fetch**:
   ```bash
   python fetch_weather_data.py
   ```
   or
   ```bash
   python fetch_data.py
   ```
   This will retrieve weather data from the specified API and save it (e.g., `weather_data.csv`) or store it locally.

3. **Transform the data**:
   ```bash
   python transform_weather_data.py
   ```
   This step converts raw data into a more consistent format, cleans columns, handles missing data, etc.

4. **Load/Store the transformed data**  
   - **Locally**: The script might automatically generate a CSV (like `historical_weather_data.csv`) in the project folder.  
   - **AWS S3**: If configured, the script can upload the CSV to your S3 bucket. Make sure you have the correct AWS keys in your environment.

---

## Configuration

- **Environment Variables**  
  Placed in `config.env` (or `.env`). Make sure this file is added to your `.gitignore` so you don’t push secrets to GitHub.

- **AWS Keys**  
  If you’re using AWS services (S3, Lambda, etc.), set `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` in your environment variables.  
  > **Security Tip**: Always rotate or invalidate exposed keys if they were ever publicly pushed.

- **API Keys**  
  For weather data providers (e.g., OpenWeatherMap, WeatherAPI, etc.), set `WEATHER_API_KEY` in `config.env`.

---

## Docker Instructions

This project includes `docker-compose.yml`, plus individual Dockerfiles (`Dockerfile.fetch`, `Dockerfile.transform`) for containerizing each stage of the pipeline.

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   This may spin up containers for fetching and transforming data, each with its own environment variables or command arguments.

2. **Check logs**:
   ```bash
   docker-compose logs -f
   ```
   Ensure data was fetched correctly and transformations completed.

3. **Tear down containers**:
   ```bash
   docker-compose down
   ```

> Adjust the compose file to your needs (e.g., linking containers, using volumes for CSV output, etc.).

---

## Planned Features

- **Automated Scheduling** with CRON or GitHub Actions  
- **Expanded Data Sources** for additional cities or weather APIs  
- **Improved Transformations** for custom metrics, e.g., rolling averages  
- **Integration Tests** to ensure pipeline reliability  
- **Data Visualization** or further analytics in Jupyter or a BI tool

---

## Contributing

1. **Fork** this repo.  
2. **Create** your feature branch (`git checkout -b feature/awesome-feature`).  
3. **Commit** your changes (`git commit -m 'Add some awesome feature'`).  
4. **Push** to the branch (`git push origin feature/awesome-feature`).  
5. **Open a Pull Request** and describe your changes.
