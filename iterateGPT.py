import os
import json
from urllib.parse import urlparse
from collections import Counter
import pandas as pd

# CSV file containing the list of websites
csv_file_path = 'top-1m.csv'  # Replace with the actual path to your CSV file

# Folder containing the HAR files
har_folder = 'harFiles'

# Read the CSV file to get the main site domains
df = pd.read_csv(csv_file_path, header=None)
main_site_domains = df[1].tolist()  # Assuming the URLs are in the second column (index 1)

# Counter for total number of third-party requests
total_requests_tp = 0

# Dictionary to count occurrences of third-party domain names
third_parties_list = Counter()

# Dictionary to store third-party cookies
third_party_cookies = Counter()

# Iterate through the HAR files
for har_file_name in os.listdir(har_folder):
    har_file_path = os.path.join(har_folder, har_file_name)
    if os.path.isfile(har_file_path) and har_file_name.endswith('.har'):
        # Extract row number from the HAR file name
        row_number = int(har_file_name.split('_')[1].split('.')[0])

        # Get the corresponding main site domain from the CSV file
        main_site_domain = main_site_domains[row_number - 1]

        with open(har_file_path, 'r', encoding='utf-8') as har_file:
            har_data = json.load(har_file)

        # Iterate through the entries in the HAR file
        for entry in har_data['log']['entries']:
            url = entry['request'].get('url', [])

            # If second-level domain not part of the URL, it is a third-party request
            if main_site_domain not in url:
                # Increment the counter for third-party domains
                total_requests_tp += 1

                # Count the occurrences of the third-party domain name to determine the top 10
                domain = urlparse(url).hostname
                if domain:
                    third_parties_list[domain] += 1

                # Extract and analyze cookies associated with third-party domains
                cookies = entry['request']['cookies']
                for cookie in cookies:
                    cookie_domain = cookie.get('domain', '')
                    if main_site_domain not in cookie_domain:
                        third_party_cookies[cookie['name']] += 1

# Report the total number of third-party requests
print("\nTotal number of third-party requests:", total_requests_tp)

# Identify the top 10 most commonly seen third-party domains
top_third_party_domains = third_parties_list.most_common(10)

print("\nTop 10 most commonly seen third-party domains:")
for i, (domain, count) in enumerate(top_third_party_domains, start=1):
    print(f"{i}. {domain}: {count} occurrences")

# Identify the top 10 most commonly seen third-party cookies
top_third_party_cookies = third_party_cookies.most_common(10)

print("\nTop 10 most commonly seen third-party cookies:")
for i, (cookie_name, count) in enumerate(top_third_party_cookies, start=1):
    print(f"{i}. {cookie_name}: {count} occurrences")