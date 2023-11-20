import os
from selenium import webdriver
from browsermobproxy import Server
import pandas as pd
import time

# Load the list of sites from the CSV file
csv_file_path = 'top-1m.csv'  # Replace with the actual path to your CSV file
df = pd.read_csv(csv_file_path, header=None)
top_sites = df[1].tolist()  # Assuming the URLs are in the second column (index 1)

# Create a folder for saving HAR files
output_folder = 'gptHarFiles'
os.makedirs(output_folder, exist_ok=True)

# Start BrowserMob Proxy server
server = Server(path='browsermob-proxy/bin/browsermob-proxy')  # Replace with the actual path to browsermob-proxy
server.start()
proxy = server.create_proxy()

# Configure Chrome options with proxy settings
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--proxy-server={proxy.proxy}')

# Create a WebDriver instance with the configured Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Set the limit for the number of sites to process
sites_limit = 1000
sites_processed = 0

# Iterate through the top sites and capture HAR files
for index, site in enumerate(top_sites, start=1):
    try:
        # Start capturing network traffic
        proxy.new_har(options={'captureHeaders': True, 'captureContent': True})
        
        # Navigate to the site
        driver.get('http://' + site)
        
        # Wait for the page to load (you may need to adjust the sleep time)
        time.sleep(5)
        
        # Save the HAR file with a unique name based on the row number
        har_file_path = os.path.join(output_folder, f'har_{index}.har')
        with open(har_file_path, 'w', encoding='utf-8') as har_file:
            har_file.write(str(proxy.har))
        
        print(f'HAR file generated for {site}: {har_file_path}')
        
        # Increment the counter
        sites_processed += 1
        
        # Check if the limit is reached
        if sites_processed >= sites_limit:
            break
    
    except Exception as e:
        print(f'Error capturing HAR for {site}: {str(e)}')

# Stop the WebDriver and BrowserMob Proxy
driver.quit()
server.stop()