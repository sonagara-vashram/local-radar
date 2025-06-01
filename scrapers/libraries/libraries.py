import requests
from bs4 import BeautifulSoup
from scrapers._common import get_headers

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
        for i in range(len(soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration'))):
            item = {}
            try:
                name_tag = soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')[i].find('div', class_='dbg0pd').find('span', class_='OSrXXb')
                item["name"] = name_tag.text.strip() if name_tag else ""
            except:
                item["name"] = ""

            try:
                type_tag = soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')[i].find('div',class_='rllt__details').find_all('div')[1]
                library_content = type_tag.text.strip() if type_tag else ""
                item['ratingCount'] = library_content.split('·')[0].strip() if '·' in library_content else ""
                item['ratingType'] = library_content.split('·')[1].strip() if '·' in library_content else ""
            except:
                item["ratingCount"] = ""
                item["ratingType"] = ""

            try:
                location_tag = soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')[i].find('div', class_='rllt__details').find_all('div')[2]
                location = location_tag.text.strip() if location_tag else ""
                item["location"] = location.split("·")[0] if location_tag else ""
            except:
                item["location"] = ""

            try:
                status_tag = soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')[i].find('div', class_='rllt__details').find_all('div')[3].find('span')
                item["status"] = status_tag.text.strip().split('⋅')[0].strip() if status_tag else ""
            except:
                item["status"] = ""

            try:
                contact_tag = soup.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')[i].find('div', class_='rllt__details').find_all('div')[2]
                item["contact"] = contact_tag.text.strip().split('·')[1].strip() if '·' in contact_tag.text else ""

            except:
                item["contact"] = ""

            extracted_data.append(item)
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
    location = location.strip().replace(" ", "+")
    url = f'https://www.google.com/search?tbm=lcl&q=libraries+in+{location}'
    html_content = get_request(url)
    if html_content:
        data = scrape_data(html_content)
        return data
    else:
        return None