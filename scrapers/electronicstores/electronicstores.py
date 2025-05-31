import requests
from bs4 import BeautifulSoup
from scrapers._common import get_headers
import re
    
def get_request(url):
    """Fetch HTML content from the given URL with error handling."""
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        return None
    
def extract_data(soup):
    """Extract Hotel data from a single result block."""
    extracted_data = []
    try:
        for i in range(len(soup.find_all("div", class_="rllt__details"))):
            item_data = {}
            try:
                name_tag = soup.find_all("div", class_="rllt__details")[i].find("div", role="heading").find("span").text.strip()
                item_data["name"] = name_tag
            except:
                item_data["name"] = ""

            try:
                rating_tag = soup.find_all("div", class_="rllt__details")[i].find("span", class_="Y0A0hc").find("span", class_="yi40Hd").text.strip()
                item_data["ratingInStar"] = rating_tag
            except:
                item_data["ratingInStar"] = ""

            try:
                count_tag = soup.find_all("div", class_="rllt__details")[i].find("span", class_="Y0A0hc").find("span", class_="RDApEe").text.strip().replace('(', '').replace(')', '')
                item_data["ratingCount"] = count_tag
            except:
                item_data["ratingCount"] = ""

            try:
                store_type_tag = soup.find_all("div", class_="rllt__details")[i].find_all("div")[1].text.strip().split("·")[1].strip()
                item_data["storeType"] = store_type_tag
            except:
                item_data["storeType"] = ""

            try:
                loc_tag = soup.find_all("div", class_="rllt__details")[i].find_all("div")[2].text.strip()
                if 'business' in loc_tag:
                    loc_tag = loc_tag.split("business")[1].replace('· ', '').strip()
                item_data["location"] = loc_tag
            except:
                item_data["location"] = ""

            try:
                contact_tag = soup.find_all("div", class_="rllt__details")[i].find_all("div")[3].text.strip().split("·")[1].strip()
                # remove strings that are not phone numbers
                contact_tag = re.sub(r"[^0-9+\-()]", "", contact_tag)
                
                item_data["contact"] = contact_tag
            except:
                item_data["contact"] = ""

            extracted_data.append(item_data)
        return extracted_data
    except AttributeError:
        return None

def scrape_data(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    data = extract_data(soup)
    if data:
        return data
    return None

def main(location):
    location = location.strip().replace(" ", "+").replace(',', '+')
    pattern = r'\b(\w+(?:\s\w+)*)\b(?:,\s\1\b)+'
    location = re.sub(pattern, r'\1', location)
    url = f'https://www.google.com/search?tbm=lcl&q=electronic+stores+{location}'
    html_content = get_request(url)
    if html_content:
        data = scrape_data(html_content)
        return data
    else:
        return None