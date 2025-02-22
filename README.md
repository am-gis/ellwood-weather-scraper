# Ellwood Weather Scraper

The purpose of this GitHub repository is to query and archive historical weather data at two locations within Ellwood Mesa Open Space, located in Goleta, CA.
As part of the [Monarch Butterfly Habitat Management Plan Implementation Phase 1](https://www.cityofgoleta.org/play/parks-recreation-open-spaces/ellwood-mesa-and-monarch-butterfly-habitat/ellwood-improvement-projects/butterfly-habitat-plan-implementation), we are required to track wind speeds within Ellwood Main butterfly grove and report on conditions annually.
The specific success criteria is "95% of wind speeds are less than 9 mph in the monarch sites (measuring every 15 minutes)."

## Weather stations

There are two cellularly enabled KestrelMet 6000 weather stations installed at Ellwood Mesa. One is located within the main grove, near the viewing area. The other is installed outside the grove, providing data to compare how the microclimate within the grove compares to the outside.

| Ellwood Main (Butterfly Grove)                                                                          | Ellwood Mesa (Reference)                                                                                |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| ![](images/ellwood_main.jpeg)                                                                           | ![](images/ellwood_mesa.jpeg)                                                                           |
| [Ambient Weather Network (Best)](https://ambientweather.net/dashboard/b4aaf46123aed035e752a9c6d12b4270) | [Ambient Weather Network (Best)](https://ambientweather.net/dashboard/20dc1ae4e73e07c0ab9ad164ebee448d) |
| [Weather Underground](https://www.wunderground.com/dashboard/pws/KCAGOLET176)                           | [Weather Underground](https://www.wunderground.com/dashboard/pws/KCAGOLET177)                           |
| [PWS Weather](https://www.pwsweather.com/station/pws/ellwoodmain)                                       | [PWS Weather](https://www.pwsweather.com/station/pws/ellwoodmesa)                                       |

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
