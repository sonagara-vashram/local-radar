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
    
def extract_data(result):
    try:
        result_data = result.find('div', class_='rllt__details').find_all('div')
        if len(result_data) >= 5:
            return None
        try:
            name = result.find('span', class_='OSrXXb')
        except: pass
        
        if not name:
            return None
        name_text = name.text.strip().replace("| ", '')
        
        try:
            rating_in_star = result.find('span', class_='yi40Hd YrbPuc')
            rating_in_star = rating_in_star.text.strip() if rating_in_star else ""
        except: pass

        try:
            rating_count = result.find('span', class_='RDApEe YrbPuc')
            rating_count = rating_count.text.strip('()') if rating_count else ""
        except: pass

        college_type = None
        type_span = name.find_next('div')
        try:
            if type_span:
                text_parts = list(type_span.stripped_strings)
                if text_parts:
                    college_type = text_parts[-1].replace('· ', '').strip()
        except:
            college_type = ""
        
        try:
            location = None
            location_type = result.find('div', class_='rllt__details').find_all('div')
            location = location_type[-2].text.strip()
        except: location = ""
        
        contact = location_type[-1]
        try:
            if contact:
                contact_text = contact.text.strip().split('· ')[-1]
                if all(char.isdigit() or char.isspace() for char in contact_text):
                    contact = contact_text
                else:
                    contact = ""
            else:
                contact = ""
        except:
            contact = ""

        if "My Ad Centre" in name_text:
            return None
        return {
            'name': name_text,
            'ratingInStar': rating_in_star,
            'ratingCount': rating_count,
            'collegeType': college_type or "",
            'contact': contact,
            'location': location,
        }
    except AttributeError:
        return None

def scrape_data(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    extracted_data = []
    results = soup.find_all('div', class_='uMdZh tIxNaf alUjuf')
    for result in results:
        # remove sponsored results
        sponsored = result.find('span', class_='pXf2tf U3A9Ac qV8iec')
        if sponsored in result:
            continue
        data = extract_data(result)
        if data:
            extracted_data.append(data)
    return extracted_data

def main(location):
    location = location.strip().replace(" ", "+")
    url = f'https://www.google.com/search?tbm=lcl&q=colleges+in+{location}'
    html_content = get_request(url)
    if html_content:
        data = scrape_data(html_content)
        return data
    else:
        return None