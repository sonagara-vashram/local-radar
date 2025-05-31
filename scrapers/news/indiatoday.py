import re
from newspaper import Article
import requests

def get_request(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    return None

def extract_urls(data):
    urls = []
    for item in data['content']:
        urls.append(item['full_url'])
    return urls

def clean_text(text):
    if text:
        text = re.sub(r'<.*?>', '', text)  
        text = re.sub(r'[^\w\s@.,&-]', '', text)
        text = text.replace('\n', '').replace('\r', '')
        return text.strip()
    return text

def extract_data(url):
    datalist = []
    
    response = get_request(url)
    urls = extract_urls(response)
    if len(urls) >= 5:
        urls = urls[:5]
    for url in urls:
        article = Article(url)
        article.download()
        article.parse()
        article.text
        obj = {
            "title": clean_text(article.title) if article.title else "",
            "text": clean_text(article.text) if article.text else "",
            "authors": clean_text(article.authors) if article.authors else "",
            "publish_date": clean_text(str(article.publish_date)) if article.publish_date else "",
        }    
        datalist.append(obj)
    return datalist if datalist else None

def main(location):
    location = location.strip().replace(" ", "+").lower()
    url = f"https://searchfeeds.intoday.in/scripts/api/index.php/group-search-suggestion?q={location}&lang=en"
    data = extract_data(url)
    return data