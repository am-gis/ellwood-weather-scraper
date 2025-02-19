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
STATIONS = {
    'ellwood_main': {
        'name': 'Ellwood Main',
        'mac_address': None  # To be filled with actual MAC address
    },
    'ellwood_mesa': {
        'name': 'Ellwood Mesa',
        'mac_address': None  # To be filled with actual MAC address
    }
}

def get_yesterday_data(mac_address, retries=3, delay=5):
    """Fetch the previous day's data for a specific station."""
    params = {
        'apiKey': API_KEY,
        'applicationKey': APPLICATION_KEY,
        'endDate': datetime.now(PACIFIC_TZ).strftime('%Y-%m-%d'),
        'limit': 100  # Adjust based on observation frequency
    }
    
    url = f"{BASE_URL}/{mac_address}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise Exception(f"Failed to fetch data after {retries} attempts: {str(e)}")
            time.sleep(delay)

def convert_to_local_time(utc_str):
    """Convert UTC timestamp to Pacific Time."""
    utc_dt = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(PACIFIC_TZ)

def process_station_data(station_id, data):
    """Process and save station data to CSV."""
    if not data:
        return
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Convert timestamps
    df['local_time'] = df['dateutc'].apply(convert_to_local_time)
    df['date'] = df['local_time'].dt.date
    
    # Create daily file
    yesterday = datetime.now(PACIFIC_TZ) - timedelta(days=1)
    file_name = f"{station_id}_{yesterday.strftime('%Y_%m_%d')}.csv"
    file_path = os.path.join(DATA_DIR, file_name)
    
    # Create directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Save to CSV, avoiding duplicates if file exists
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        df = pd.concat([existing_df, df]).drop_duplicates(subset=['dateutc'])
    
    df.to_csv(file_path, index=False)
    return file_path

def main():
    """Main function to fetch and process weather data."""
    for station_id, station_info in STATIONS.items():
        if not station_info['mac_address']:
            print(f"Warning: MAC address not configured for {station_info['name']}")
            continue
            
        try:
            data = get_yesterday_data(station_info['mac_address'])
            file_path = process_station_data(station_id, data)
            print(f"Successfully processed data for {station_info['name']}: {file_path}")
        except Exception as e:
            print(f"Error processing {station_info['name']}: {str(e)}")
            raise

if __name__ == '__main__':
    main()