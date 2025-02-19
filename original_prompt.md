You are tasked with developing a Python-based solution that retrieves and stores weather observations from two personal weather stations (PWS) on the Ambient Weather Network (AWN). These stations are located at Ellwood Mesa near Santa Barbara, CA. The data is crucial for monitoring wind speeds and other conditions during the monarch overwintering period (October–March). However, the script should run year-round for now.

1. Stations & Data Retrieval
Two Stations

Station A: "Ellwood Main" (provide unique device MAC or identifier)
Station B: "Ellwood Mesa" (provide unique device MAC or identifier)
Data Source & API

Use the AWN API at https://rt.ambientweather.net/v1/devices/...
Each station has a unique identifier (e.g., 30:71:25:91:27:32).
The request includes two keys: apiKey (which may change) and applicationKey (likely stable).
API credentials should be stored securely:
Locally: in a .env file.
In GitHub Actions: as GitHub Secrets.
Daily Retrieval

The script should run once daily (e.g., shortly after midnight local time).
For each station, fetch the previous day’s data in full.
Use appropriate query parameters for date range or limit to ensure all observations (about every 15 minutes) are captured for the prior 24 hours.
Retry Logic: If the API call fails, attempt a reasonable number of retries before logging an error and exiting.
Timestamp & Local Time

Convert AWN’s UTC timestamps into local time (Santa Barbara, CA).
Store date and time in the resulting CSV. Do not store empty rows or placeholders if data is missing.
2. Data Storage (Daily CSV Files)
Per-Day, Per-Station CSV

Create a new CSV file each day for each station.
Example naming convention: ellwood_main_YYYY_MM_DD.csv and ellwood_mesa_YYYY_MM_DD.csv.
Place all CSV files in a subdirectory (e.g., data/).
Fields

For every JSON field returned (e.g., dateutc, windspeedmph, windgustmph, humidity, etc.), store it in the CSV.
Convert numeric fields from strings if needed.
Retain the original UTC timestamp and the converted local time in the CSV to avoid confusion.
Deduplication

Before appending a record, check for duplicates by using a unique timestamp (e.g., dateutc) as the key.
If a record with the same dateutc exists in the CSV, skip it to avoid duplication.
Repository Storage

Commit the CSV files to the GitHub repository.
There is no archiving or purging strategy at the moment—simply keep all files.
3. GitHub Actions Workflow
Workflow File

Provide a GitHub Actions YAML (e.g., .github/workflows/scraper.yml) that:
Runs daily (once every 24 hours, near local midnight).
Installs dependencies.
Loads secrets (API key, application key) as environment variables.
Executes the Python script.
Commits any newly created CSV files to the repository.
Environment Variable Management

Use GitHub Secrets for API_KEY and APPLICATION_KEY.
Load them in the workflow and pass them to the Python script via environment variables.
Error Logging & Notifications

Log errors in the GitHub Actions console if the script fails or the API is unreachable (after retries).
Provide a clear exit code to indicate success/failure.
4. Code Structure & Extras
Python Code Requirements

Use a requirements.txt for dependency management.
Provide a well-commented, modular Python script that:
Loads .env locally or GitHub Secrets in production.
Constructs the AWN API calls for each station.
Fetches the previous day’s data (or enough records to cover ~24 hours).
Converts UTC timestamps to local time (Pacific Time).
Deduplicates and appends new rows to a daily CSV for each station.
Handles retries for failed API requests.
Logs errors and successes.
README.md

Include a brief setup guide:
How to install dependencies.
How to configure the .env file.
How to run the script locally.
An overview of the CSV output.
Explanation of the GitHub Actions workflow.
Future-Proofing

Keep the design modular so future scrapers (e.g., WeatherUnderground, PWSweather) can be added with minimal refactoring.
Possibly use a helper function or config to manage multiple stations.
5. Deliverables
Please provide:

A single Python script (or a small set of Python modules) implementing the above functionality.
A requirements.txt file.
A README.md with instructions and usage notes.
A GitHub Actions workflow file in .github/workflows/scraper.yml that runs daily and commits CSV files to the repository.
Focus on clarity, maintainability, and robust error handling. Do not include placeholder rows for missing data. Keep the code and documentation concise yet thorough enough for a handoff to non-technical coworkers who may rely on LLM assistance.