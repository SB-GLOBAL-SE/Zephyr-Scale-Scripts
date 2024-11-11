import csv
import requests
from requests.auth import HTTPBasicAuth

# Replace with your basic auth credentials
username = '<>'

password = '<>'

# Replace with your host
host = '<>'

# Replace with your projectKey it must be in all caps IE: ZULU
projectKey = '<>'

# The CSV file path (since it's in the same directory as the script)
csv_file_path = 'inputfileTestCycle.csv'

# API endpoint template
url_template = f'{host}/rest/atm/1.0/testrun'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Read the CSV file
try:
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Iterate through each row in the CSV
        for row in csv_reader:
            cycleName = row['Test_cycle_name']  # Extract test case key from the CSV
            owner = row['username']
            folder = row["Folder"]
            folder = f"/{folder}"
            plannedStartDate = row['planned_start_date']
            plannedEndDate = row['planned_end_date']

            
            # Define the payload for the API request using CSV data
            payload = {
                "name": cycleName,
                "projectKey": projectKey,
                "folder": folder,
                "owner": owner,
                "plannedStartDate": plannedStartDate,
                "plannedEndDate": plannedEndDate
            }
            

            # Create the URL for the specific test case
            url = url_template

            # Send the POST request
            response = requests.post(url, json=payload, headers=headers, auth=HTTPBasicAuth(username, password))

            # Print response status for each request
            if response.status_code == 201:
                print(f'Successfully created {cycleName}')
            else:
                print(f'Error creating {cycleName}: {response.status_code} - {response.content}')
                print(payload)
                print(url)
except FileNotFoundError:
    print(f"CSV file '{csv_file_path}' not found.")