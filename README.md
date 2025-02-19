# ellwood-weather-scraper

Automated weather data scraper for two personal weather stations at Ellwood Mesa, logging daily observations for monarch overwintering habitat monitoring.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kylenessen/ellwood-weather-scraper.git
   cd ellwood-weather-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Create a `.env` file in the project root with:
     ```
     API_KEY=your_ambient_weather_api_key
     APPLICATION_KEY=your_ambient_weather_application_key
     ```
   - For GitHub Actions, set these as repository secrets:
     - `API_KEY`
     - `APPLICATION_KEY`

4. Configure station MAC addresses:
   - Open `src/weather_scraper.py`
   - Update the `STATIONS` dictionary with your station MAC addresses

## Usage

### Local Execution
Run the script manually:
```bash
python src/weather_scraper.py
```

### Automated Execution
The script runs automatically via GitHub Actions:
- Schedule: Daily at 12:15 AM Pacific Time
- Stores data in CSV files under the `data/` directory
- Automatically commits new data files to the repository

## Data Output

CSV files are generated daily for each station:
- Format: `{station_id}_{YYYY}_{MM}_{DD}.csv`
- Location: `data/` directory
- Contains:
  - UTC and local timestamps
  - All weather measurements from the stations
  - No placeholder rows for missing data

## Error Handling

- Failed API requests are retried up to 3 times
- Errors are logged to GitHub Actions console
- Duplicate data points are automatically filtered

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

[Add your license information here]
