from browsermobproxy import Server
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
import json
import csv
import os

# create a browsermob server instance
server = Server("browsermob-proxy/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy(params=dict(trustAllServers=True))

timeout = 60
# create a new chromedriver instance
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=chrome_options)


output_folder = 'harFiles'
os.makedirs(output_folder, exist_ok=True)

csv_path = "top-1m.csv"
count = 0
ind = 1
nSites = 1000
skipped = 0 

# do crawling
file = open(csv_path, 'r')
csv_reader = csv.reader(file)

for row in csv_reader:

        if count == nSites:
            break

        try:
            website = "http://" + row[1]
            print(f"{ind} Website is {website}")

            
            proxy.new_har(f"har_{ind}", options={'captureHeaders': True, 'captureContent': True, 'captureCookies': True})
            driver.set_page_load_timeout(timeout)
            driver.get(website)

            # write har file
            file_path = os.path.join(output_folder, f"har_{ind}.har")
            with open(file_path, 'w') as singleObject:
                singleObject.write(json.dumps(proxy.har))

            ind+= 1
            count += 1
            
        except (TimeoutException, WebDriverException) as e:
            print(f"Error accessing {ind} {website}: {str(e)}")
            skipped += 1
            print(f"skipped files {skipped}")
            ind+= 1

        except Exception as e:
            print(f"Unexpected error accessing {ind} {website}: {str(e)}")
            skipped += 1
            print(f"skipped files {skipped}")
            ind+= 1

        except ConnectionRefusedError as e:
            print(f"Connection refused error accessing {ind} {website}: {str(e)}")
            skipped += 1
            print(f"skipped files {skipped}")
            ind+= 1
            

# Reset 
driver.set_page_load_timeout(0)
# stop server and exit
file.close()
server.stop()
driver.quit()
       
