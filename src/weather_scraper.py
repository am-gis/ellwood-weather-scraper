import os
import json
import time
from datetime import datetime, timedelta
import pytz
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('API_KEY')
APPLICATION_KEY = os.getenv('APPLICATION_KEY')
BASE_URL = 'https://rt.ambientweather.net/v1/devices'
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Station configurations
# To configure your stations:
# 1. Find your station's MAC address from the Ambient Weather dashboard
# 2. Set them in your environment variables
# Example MAC format: "XX:XX:XX:XX:XX:XX" (replace X with actual values)
STATIONS = {
    'ellwood_main': {
        'name': 'Ellwood Main',
        # Set in .env file or GitHub Secrets
        'mac_address': os.getenv('ELLWOOD_MAIN_MAC')
    },
    'ellwood_mesa': {
        'name': 'Ellwood Mesa',
        # Set in .env file or GitHub Secrets
        'mac_address': os.getenv('ELLWOOD_MESA_MAC')
    }
}

# Validate station configurations
for station_id, info in STATIONS.items():
    if not info['mac_address']:
        print(f"Warning: MAC address not configured for {info['name']}. "
              f"Set {station_id.upper()}_MAC in your environment variables.")


def get_two_days_ago_data(mac_address, retries=3, delay=5):
    """Fetch the previous day's data for a specific station."""
    # Calculate yesterday's date in Pacific Time
    today_midnight = datetime.now(PACIFIC_TZ).replace(
        hour=0, minute=0, second=0, microsecond=0)
    yesterday_midnight = today_midnight - timedelta(days=1)
    two_days_ago_midnight = today_midnight - timedelta(days=2)

    # Convert to UTC for API request
    end_time_utc = yesterday_midnight.astimezone(pytz.UTC)
    start_time_utc = two_days_ago_midnight.astimezone(pytz.UTC)

    params = {
        'apiKey': API_KEY,
        'applicationKey': APPLICATION_KEY,
        'endDate': end_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'startDate': start_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'mac': mac_address,
        'limit': 288  # Get 24 hours of data assuming 5-minute intervals
    }

    url = f"{BASE_URL}/{mac_address}"

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Print sample of raw data for debugging
            if data:
                print(f"Raw data sample for {mac_address}: {data[0]}")

                # Filter data to ensure it's within yesterday's range
                filtered_data = [
                    record for record in data
                    if two_days_ago_midnight <= convert_to_local_time(record['dateutc']) < today_midnight
                ]
                data = filtered_data
                print(f"Number of records received: {len(data)}")

            return data
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise Exception(
                    f"Failed to fetch data after {retries} attempts: {str(e)}")
            print(
                f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)


def convert_to_local_time(utc_value):
    """Convert UTC timestamp to Pacific Time."""
    if isinstance(utc_value, (int, float)):
        # Handle Unix timestamp (convert from milliseconds to seconds if needed)
        try:
            # First try assuming it's in seconds
            utc_dt = datetime.fromtimestamp(utc_value, pytz.UTC)
        except (ValueError, OSError):
            # If that fails, try converting from milliseconds
            try:
                utc_dt = datetime.fromtimestamp(utc_value / 1000, pytz.UTC)
            except (ValueError, OSError) as e:
                print(f"Error parsing timestamp {utc_value}: {e}")
                return None
    else:
        try:
            # Try ISO format first
            utc_dt = datetime.strptime(utc_value, '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_dt = pytz.utc.localize(utc_dt)
        except (ValueError, TypeError):
            # If that fails, try Unix timestamp as string
            try:
                timestamp = float(utc_value)
                # Check if timestamp is in milliseconds (13 digits) or seconds (10 digits)
                if len(str(int(timestamp))) > 10:
                    timestamp = timestamp / 1000
                utc_dt = datetime.fromtimestamp(timestamp, pytz.UTC)
            except (ValueError, TypeError, OSError) as e:
                print(f"Error parsing timestamp {utc_value}: {e}")
                return None
    return utc_dt.astimezone(PACIFIC_TZ)


def process_station_data(station_id, data):
    """Process and save station data to CSV."""
    if not data:
        print(f"No data received for station {station_id}")
        return

    print(f"Sample data for {station_id}:", data[0] if data else None)

    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Print timestamp format for debugging
        print(
            f"First timestamp value: {df['dateutc'].iloc[0]} (type: {type(df['dateutc'].iloc[0])})")

        # Convert timestamps
        df['local_time'] = df['dateutc'].apply(convert_to_local_time)
        # Print first converted timestamp for verification
        if not df['local_time'].isna().all():
            print(f"First converted timestamp: {df['local_time'].iloc[0]}")

        # Remove rows where timestamp conversion failed
        df = df.dropna(subset=['local_time'])
        if df.empty:
            print(
                f"No valid data after timestamp conversion for station {station_id}")
            return

        df['date'] = df['local_time'].dt.date

        # Create daily file
        two_days_Ago = (datetime.now(PACIFIC_TZ)
                     .replace(hour=0, minute=0, second=0, microsecond=0)
                     - timedelta(days=2))
        file_name = f"{station_id}_{two_days_ago.strftime('%Y_%m_%d')}.csv"
        file_path = os.path.join(DATA_DIR, file_name)

        # Create directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Save to CSV, avoiding duplicates if file exists
        if os.path.exists(file_path):
            try:
                existing_df = pd.read_csv(file_path)
                df = pd.concat([existing_df, df]).drop_duplicates(
                    subset=['dateutc'])
            except Exception as e:
                print(
                    f"Warning: Error reading existing CSV for {station_id}: {e}")
                # Continue with just the new data if there's an error reading existing file

        df.to_csv(file_path, index=False)
        return file_path

    except Exception as e:
        print(f"Error processing data for station {station_id}: {e}")
        raise


def main():
    """Main function to fetch and process weather data."""
    for station_id, station_info in STATIONS.items():
        if not station_info['mac_address']:
            print(
                f"Warning: MAC address not configured for {station_info['name']}")
            continue

        try:
            data = get_two_days_ago_data(station_info['mac_address'])
            file_path = process_station_data(station_id, data)
            print(
                f"Successfully processed data for {station_info['name']}: {file_path}")
        except Exception as e:
            print(f"Error processing {station_info['name']}: {str(e)}")
            raise


if __name__ == '__main__':
    main()
