# %% [markdown]
# # Weather Station Data Analysis
#
# This notebook fetches and analyzes historical data from Ellwood weather stations.

# %% Imports
import os
import json
import time
from datetime import datetime, timedelta
import pytz
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# %% Configuration
# Configuration
API_KEY = os.getenv('API_KEY')
APPLICATION_KEY = os.getenv('APPLICATION_KEY')
BASE_URL = 'https://rt.ambientweather.net/v1/devices'
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')

# Station configurations
STATIONS = {
    'ellwood_main': {
        'name': 'Ellwood Main',
        'mac_address': os.getenv('ELLWOOD_MAIN_MAC')
    },
    'ellwood_mesa': {
        'name': 'Ellwood Mesa',
        'mac_address': os.getenv('ELLWOOD_MESA_MAC')
    }
}

# %% Functions


def get_historical_data(mac_address, start_date, end_date, retries=3, delay=5):
    """Fetch historical data for a specific station between two dates."""
    # Convert dates to UTC for API request
    start_time_utc = start_date.astimezone(pytz.UTC)
    end_time_utc = end_date.astimezone(pytz.UTC)

    params = {
        'apiKey': API_KEY,
        'applicationKey': APPLICATION_KEY,
        'endDate': end_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'startDate': start_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'mac': mac_address,
        'limit': 288  # Maximum records per request
    }

    url = f"{BASE_URL}/{mac_address}"
    all_data = []

    current_start = start_time_utc
    while current_start < end_time_utc:
        current_end = min(current_start + timedelta(days=1), end_time_utc)
        params['startDate'] = current_start.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        params['endDate'] = current_end.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        for attempt in range(retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                all_data.extend(data)
                break
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise Exception(
                        f"Failed to fetch data after {retries} attempts: {str(e)}")
                print(
                    f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)

        current_start = current_end
        time.sleep(1)  # Rate limiting

    return all_data


def convert_to_local_time(utc_value):
    """Convert UTC timestamp to Pacific Time."""
    if isinstance(utc_value, (int, float)):
        try:
            utc_dt = datetime.fromtimestamp(utc_value, pytz.UTC)
        except (ValueError, OSError):
            try:
                utc_dt = datetime.fromtimestamp(utc_value / 1000, pytz.UTC)
            except (ValueError, OSError) as e:
                print(f"Error parsing timestamp {utc_value}: {e}")
                return None
    else:
        try:
            utc_dt = datetime.strptime(utc_value, '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_dt = pytz.utc.localize(utc_dt)
        except (ValueError, TypeError):
            try:
                timestamp = float(utc_value)
                if len(str(int(timestamp))) > 10:
                    timestamp = timestamp / 1000
                utc_dt = datetime.fromtimestamp(timestamp, pytz.UTC)
            except (ValueError, TypeError, OSError) as e:
                print(f"Error parsing timestamp {utc_value}: {e}")
                return None
    return utc_dt.astimezone(PACIFIC_TZ)


# %% Data Download
# Set the date range for historical data
end_date = datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=0)
start_date = end_date - timedelta(days=7)

print(f"Fetching data from {start_date} to {end_date}")

# Fetch data for each station
all_station_data = {}

for station_id, station_info in STATIONS.items():
    if not station_info['mac_address']:
        print(
            f"Warning: MAC address not configured for {station_info['name']}")
        continue

    print(f"Fetching data for {station_info['name']}...")
    try:
        data = get_historical_data(
            station_info['mac_address'], start_date, end_date)

        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['local_time'] = df['dateutc'].apply(convert_to_local_time)
        df = df.dropna(subset=['local_time'])

        if not df.empty:
            df['date'] = df['local_time'].dt.date
            all_station_data[station_id] = df
            print(
                f"Successfully fetched {len(df)} records for {station_info['name']}")
        else:
            print(f"No valid data found for {station_info['name']}")

    except Exception as e:
        print(f"Error processing {station_info['name']}: {str(e)}")

# %% Build Dataframe

# Combine all station data into a single DataFrame
combined_df = pd.concat(
    [df.assign(station=station_id)
     for station_id, df in all_station_data.items()],
    ignore_index=True
)

# Sort by station and timestamp
df = combined_df.sort_values(['station', 'local_time'])
# Select and reorder key columns
df = df[[
    'local_time',
    'station',
    'tempf',
    'humidity',
    'windspeedmph',
    'windgustmph',
    'winddir',
    'solarradiation',
    'solarradday',
    'batt1volts'
]]

df
# %%

# Print diagnostic information
print("Checking for null values in battery voltage data:")
for station in ['ellwood_main', 'ellwood_mesa']:
    station_data = df[df['station'] == station]
    null_count = station_data['batt1volts'].isnull().sum()
    total_count = len(station_data)
    print(f"{station}: {null_count} null values out of {total_count} records")
    print(
        f"Battery voltage range: {station_data['batt1volts'].min():.2f} to {station_data['batt1volts'].max():.2f}")

# Create the plots with null handling
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
fig.suptitle('Solar Radiation and Battery Voltage by Station', fontsize=16)

# Colors for consistency
solar_color = 'orange'
battery_color = 'blue'

# Plot for Ellwood Main
main_data = df[df['station'] == 'ellwood_main'].dropna(
    subset=['batt1volts', 'solarradiation'])
ax1_twin = ax1.twinx()

ax1.plot(main_data['local_time'], main_data['solarradiation'],
         color=solar_color, label='Solar Radiation')
ax1_twin.plot(main_data['local_time'], main_data['batt1volts'],
              color=battery_color, label='Battery Voltage')

ax1.set_title('Ellwood Main')
ax1.set_xlabel('Local Time')
ax1.set_ylabel('Solar Radiation (W/m²)', color=solar_color)
ax1_twin.set_ylabel('Battery Voltage (V)', color=battery_color)

# Plot for Ellwood Mesa
mesa_data = df[df['station'] == 'ellwood_mesa'].dropna(
    subset=['batt1volts', 'solarradiation'])
ax2_twin = ax2.twinx()

ax2.plot(mesa_data['local_time'], mesa_data['solarradiation'],
         color=solar_color, label='Solar Radiation')
ax2_twin.plot(mesa_data['local_time'], mesa_data['batt1volts'],
              color=battery_color, label='Battery Voltage')

ax2.set_title('Ellwood Mesa')
ax2.set_xlabel('Local Time')
ax2.set_ylabel('Solar Radiation (W/m²)', color=solar_color)
ax2_twin.set_ylabel('Battery Voltage (V)', color=battery_color)

# Add legends
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()
# %%
