import json
import re
import requests
from bs4 import BeautifulSoup

def get_request(url, position, location):
    """Fetch HTML content from the given URL with error handling."""
    try:
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-IN,en;q=0.9',
            'appid': '109',
            'content-type': 'application/json',
            'referer': f'https://www.naukri.com/{position}-jobs-in-{location}',
            'systemid': 'Naukri',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        return None

def extract_data(response):
    datalist = []
    try:
        baseurl = 'https://www.naukri.com'
        if response:
            data = json.loads(response)
            for job in data['jobDetails']:
                obj = {'title': '', "url": '', 'company': '', 'currency': '', 'postDate': '', 'skills': '', 'placeholders': [], "description": ''}
                title = job['title']
                if title: obj['title'] = title 
                else: obj['title'] = ""
                
                company = job['companyName']
                if company: obj['company'] = company
                else: obj['company'] = ""
                
                currency = job['currency']
                if currency: obj['currency'] = currency
                else: obj['currency'] = ""
                
                postDate = job['footerPlaceholderLabel']
                if postDate: obj['postDate'] = postDate
                else: obj['postDate'] = ""
                
                skills = job['tagsAndSkills']
                if skills: obj['skills'] = skills
                else: obj['skills'] = ""
                
                for i in job['placeholders']:
                    key = i['type']
                    value = i['label']
                    obj['placeholders'].append({key: value})
                    
                url = baseurl + job['jdURL']
                if url: obj['url'] = url
                else: obj['url'] = ""
                
                description = job['jobDescription'].strip().replace('\n', ' ')
                # remove all unwanted character from description using regex
                desc = re.sub(r'[^\x00-\x7F]+', ' ', description)
                # remove any html content from description
                if '<' in desc:
                    desc = BeautifulSoup(desc, "lxml").text
                    
                if desc: obj['description'] = desc.strip()
                else: obj['description'] = ""
                
                datalist.append(obj)    
        return datalist
    except Exception as e:
        pass
    return
        
def scrape_data(url):
    data = extract_data(url)
    if data:
        return data
    return None

def main(location, **kwargs):
    location = location.strip().replace(" ", "+")
    position = kwargs.get("position")
    position = position.strip().replace(" ", "%20")
    url = f'https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={location}&keyword={position}'
    response = get_request(url, position, location)
    if response:
        data = scrape_data(response)
        if data:
            return data
        return None
    else:
        return None