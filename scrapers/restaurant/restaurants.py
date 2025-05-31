from bs4 import BeautifulSoup
import requests
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
    """Extract restaurant data from a single result block."""
    try:
        try:
            name = result.find('span', class_='OSrXXb')
        except: pass
        
        if not name:
            return None
        name_text = name.text.strip().replace(' |', '')
        
        try:
            rating_in_star = result.find('span', class_='yi40Hd YrbPuc')
            rating_in_star = rating_in_star.text.strip() if rating_in_star else ""
        except: pass

        try:
            rating_count = result.find('span', class_='RDApEe YrbPuc')
            rating_count = rating_count.text.strip('()') if rating_count else ""
        except: pass

        try:
            price = None
            currency_symbols = ['₹', '$', '£', '€', '¥']
            
            for span in result.find_all('span'):
                span_text = span.text.strip()
                for symbol in currency_symbols:
                    if any(char.isdigit() for char in span.text) and symbol in span_text:
                        span_text = span_text.replace('+', '').replace(symbol, '').strip()
                        price = span_text + symbol
                        break
                if price:
                    break
        except Exception as e: pass

        restaurant_type = None
        type_span = name.find_next('div')
        try:
            if type_span:
                text_parts = list(type_span.stripped_strings)
                if text_parts:
                    restaurant_type = text_parts[-1].replace('· ', '').strip()
        except:
            restaurant_type = ""
        
        try:
            location = name.find_next('div').find_next('div')
            location = location.text.strip() if location else ""
        except: pass

        if "My Ad Centre" in name_text:
            return None
        return {
            'name': name_text,
            'ratingInStar': rating_in_star,
            'ratingCount': rating_count,
            'price': price or "",
            'restaurantType': restaurant_type or "",
            'location': location,
        }
    except AttributeError:
        return None

def scrape_data(html_content):
    """Scrape restaurant data from HTML content."""
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
    url = f'https://www.google.com/search?tbm=lcl&q=restaurant+in+{location}'
    html_content = get_request(url)
    if html_content:
        data = scrape_data(html_content)
        if data:
            return data
        return None
    else:
        return None