
## ---------------------code with pagination
import json
import os
import requests
from datetime import datetime
import matplotlib.pyplot as plt

from collections import Counter

def fetch_transit_data():
    token_file_path = os.path.join(os.path.dirname(__file__), 'token.txt')
    with open(token_file_path, 'r') as f:
        token = f.read().strip() 
    
    url = 'https://api.sparelabs.com/v1/exports/ridership'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    all_data = []

    # Fetch data page by page until all data is retrieved
    page = 1
    while True:
        params = {'limit': 50, 'skip': (page - 1) * 50}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if not data or 'data' not in data:
            break
        
        all_data.extend(data['data'])

        # If there are less than 50 records in the response, it means all data is fetched
        if len(data['data']) < 50:
            break

        page += 1

    if not all_data:
        return {}

    total_trips = len(all_data)
    status_distribution = {}
    trip_durations = []
    wait_times = []
    cancellation_reasons = {}
    mobility_types = {}
    payment_methods = {}

    pickup_addresses = []
    dropoff_addresses = []
    trip_request_timestamps = []

    for trip in all_data:
        # Trip status distribution
        status = trip['status']
        status_distribution[status] = status_distribution.get(status, 0) + 1

        # Trip duration calculation
        if trip['tripDurationSeconds'] is not None:
            trip_durations.append(trip['tripDurationSeconds'])

        # Wait time calculation
        if trip['pickupArrivedTime'] and trip['requestedPickupTime']:
            pickup_arrival_time = parse_date(trip['pickupArrivedTime'])
            requested_pickup_time = parse_date(trip['requestedPickupTime'])
            if pickup_arrival_time is not None and requested_pickup_time is not None:
                wait_time = (pickup_arrival_time - requested_pickup_time).total_seconds()
                wait_times.append(wait_time)

        # Cancellation analysis
        cancellation_reason = trip['cancellationReason']
        if cancellation_reason:
            cancellation_reasons[cancellation_reason] = cancellation_reasons.get(cancellation_reason, 0) + 1

        # Mobility type calculation
        mobility_type = trip.get('riderMetadata', {}).get('mobilityType')
        if mobility_type:
            for mobility in mobility_type:
                mobility_types[mobility] = mobility_types.get(mobility, 0) + 1

        # Payment method calculation
        payment_method = trip.get('paymentMethodType')
        if payment_method:
            payment_methods[payment_method] = payment_methods.get(payment_method, 0) + 1

        # Pickup and dropoff addresses
        pickup_addresses.append(trip.get('requestedPickupAddress'))
        dropoff_addresses.append(trip.get('requestedDropoffAddress'))

        trip_request_timestamps.append(trip['requestedPickupTime'])

    # Calculate average trip duration and wait time
    avg_trip_duration = "{:.2f}".format(sum(trip_durations) / len(trip_durations) / 60) if trip_durations else 0

    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0

    # Get top 10 pickup and dropoff addresses
    top_pickup_addresses = Counter(pickup_addresses).most_common(10)
    top_dropoff_addresses = Counter(dropoff_addresses).most_common(10)


    cancellation_reasons_json = json.dumps(cancellation_reasons)
    status_distribution_json = json.dumps(status_distribution)
    payment_methods_json = json.dumps(payment_methods)
    status_distribution_json = json.dumps(status_distribution)
    

    # Extract hours of the day from timestamp strings
    hours_of_day = [int(timestamp.split()[2].split(':')[0]) for timestamp in trip_request_timestamps]

    # Count the number of trips for each hour
    # trip_counts = [hours_of_day.count(hour) for hour in range(24)]


    return {
        'total_trips': total_trips,
        'status_distribution': status_distribution_json,
        'avg_trip_duration': avg_trip_duration,
        'avg_wait_time': avg_wait_time,
        'cancellation_reasons': cancellation_reasons_json,
        'mobility_types': mobility_types,
        'payment_methods': payment_methods,
        'payment_methods_json': payment_methods_json,
        'top_pickup_addresses': top_pickup_addresses,
        'top_dropoff_addresses': top_dropoff_addresses
    }

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None
