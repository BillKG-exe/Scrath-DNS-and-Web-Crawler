# Python program to read
# json file

# Report the number of requests made to third-party domains when visiting each site. A third-party
# domain is a domain that does not have the same second-level domain (SLD) as the site you are
# visiting. For example, when you are visiting google.com, ads.google.com is not a third-party
# since it has the same second level domain (google) as google.com. However, doubleclick.net is
# considered a third-party to google.com. Identify the top-10 most commonly seen third-parties
# across all sites.

# Identify the third-party cookies present while visiting each site. Third-party cookies are those
# cookies that were accessed (set or read) by third-party domains. Identify the top-10 most
# commonly seen third-party cookies across all sites and describe their intended functionality by
# referencing Cookiepedia.

from urllib.parse import urlparse
import json
import csv
import os

#Get the list of the collected files (index, website names)
csv_path = "top-1m.csv"
file = open(csv_path, 'r')
csv_reader = csv.reader(file)

total_requests_tp = 0
third_parties_list = {} 
third_party_cookies = {}
count = 0


for row in csv_reader:
    # Opening JSON file
    # returns JSON object as 
    # a dictionary
    if count == 1000:
        break

    if os.path.exists(f"harFiles/har_{row[0]}.har"):
        with open(f"harFiles/har_{row[0]}.har", 'r') as f:
            data = json.load(f)

        # Iterating through the json list
        count += 1
        for entry in data['log']['entries']:
            url = entry['request'].get('url', [])
            
            #If second level domain not part of the URL, it is a third-party request
            if  row[1] not in url:
                #increment our counter ot Third party domains
                total_requests_tp += 1
                
                #Count the third party domain name ocurrencies to determine the top 10
                domain = urlparse(url).hostname
                if domain in third_parties_list:
                    third_parties_list[domain] += 1
                else:
                    third_parties_list[domain] = 1

                #if third party domain,  then get the cookies
                request_cookies = entry['request'].get('cookies', [])
                response_cookies = entry['response'].get('cookies',[])

                #count the cookies occurrencies for request_cookies and response_cookies
                for cookie in request_cookies:
                    cookie_name = cookie.get('name')
                    if cookie_name in third_party_cookies:
                        third_party_cookies[cookie_name] += 1
                    else:
                        third_party_cookies[cookie_name] = 1
                
                for cookie in response_cookies:
                    cookie_name = cookie.get('name')
                    if cookie_name in third_party_cookies:
                        third_party_cookies[cookie_name] += 1
                    else:
                        third_party_cookies[cookie_name] = 1

print(f"Total requests: {total_requests_tp}")

top_10_tp = sorted(third_parties_list, key =third_parties_list.get, reverse=True)[:10]

top_10_cookies = sorted(third_party_cookies, key =third_party_cookies.get, reverse=True)[:10]


print("TOP 10 THIRD PARTIES:")
for key in top_10_tp:
    print(f" {key}: {third_parties_list[key]}" )

print("TOP 10 THIRD PARTY COOKIES:")
for key in top_10_cookies:
    print(f" {key}: {third_party_cookies[key]}" )

# Closing file
f.close()
