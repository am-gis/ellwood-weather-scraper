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

# Save data into a relative folder that works in GitHub Actions and locally
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

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

for station_id, info in STATIONS.items():
    if not info['mac_address']:
        print(f"Warning: MAC address not configured for {info['name']}. "
              f"Set {station_id.upper()}_MAC in your environment variables.")


def convert_to_local_time(utc_value):
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


def get_data_for_date(mac_address, target_date, retries=3, delay=5):
    start_local = PACIFIC_TZ.localize(datetime.combine(target_date, datetime.min.time()))
    end_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(pytz.UTC)
    end_utc = end_local.astimezone(pytz.UTC)

    params = {
        'apiKey': API_KEY,
        'applicationKey': APPLICATION_KEY,
        'endDate': end_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'startDate': start_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'mac': mac_address,
        'limit': 288
    }

    url = f"{BASE_URL}/{mac_address}"

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            filtered_data = [
                record for record in data
                if start_local <= convert_to_local_time(record['dateutc']) < end_local
            ]
            return filtered_data
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise Exception(f"Failed to fetch data after {retries} attempts: {str(e)}")
            print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)


def process_station_data(station_id, data, date_obj):
    if not data:
        print(f"No data received for station {station_id}")
        return

    try:
        df = pd.DataFrame(data)
        df['local_time'] = df['dateutc'].apply(convert_to_local_time)
        df = df.dropna(subset=['local_time'])

        if df.empty:
            print(f"No valid data after timestamp conversion for station {station_id}")
            return

        df['date'] = df['local_time'].dt.date

        file_name = f"{station_id}_{date_obj.strftime('%Y_%m_%d')}.csv"
        file_path = os.path.join(DATA_DIR, file_name)

        os.makedirs(DATA_DIR, exist_ok=True)

        if os.path.exists(file_path):
            try:
                existing_df = pd.read_csv(file_path)
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['dateutc'])
            except Exception as e:
                print(f"Warning: Error reading existing CSV for {station_id}: {e}")

        df.to_csv(file_path, index=False)
        return file_path

    except Exception as e:
        print(f"Error processing data for station {station_id}: {e}")
        raise


def main():
    start_date = datetime(2024, 5, 1).date()
    end_date = datetime(2024, 5, 8).date()

    for current_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        print(f"\nFetching data for {current_date}")
        for station_id, station_info in STATIONS.items():
            if not station_info['mac_address']:
                print(f"Warning: MAC address not configured for {station_info['name']}")
                continue

            try:
                data = get_data_for_date(station_info['mac_address'], current_date)
                file_path = process_station_data(station_id, data, current_date)
                print(f"Processed data for {station_info['name']} on {current_date}: {file_path}")
            except Exception as e:
                print(f"Error processing {station_info['name']} on {current_date}: {str(e)}")


if __name__ == '__main__':
    main()
