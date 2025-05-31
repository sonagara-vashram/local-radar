import json
import re
import requests
from bs4 import BeautifulSoup

session = requests.Session()

def login():
    USERNAME = "gaked36598@jarars.com"
    PASSWORD = "L8UaV#yATQx"
    payload = {
        "email": USERNAME,
        "password": PASSWORD,
        "candidate_id": "",
        "login_with_otp": "false",
        "otp_code": "",
        "do_not_verify_mobile": "false",
        "keep_me_signed_in": "y"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        LOGIN_URL = "https://www.shine.com/ajax/login/"
        response = session.post(LOGIN_URL, data=payload, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        return False

def get_request(url):
    try:
        response = session.get(url, timeout=20)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.RequestException as e:
        return None

def extract_ids(response):
    ids = []
    if response:
        soup = BeautifulSoup(response, 'lxml')
        script = soup.find('script', id="__NEXT_DATA__")
        if script:
            try:
                data = script.string
                json_data = json.loads(data)
                job_list = json_data['props']['pageProps']['initialState']['jsrp']['searchresult']['data']['results']
                for job in job_list:
                    ids.append(job['id'])
            except json.JSONDecodeError:
                pass
    return ids

def clean_text(text):
    if text:
        text = re.sub(r'<.*?>', '', text)  
        text = re.sub(r'[^\w\s@.,&-]', '', text) 
        return text.strip()
    return text

def extract_data(url):
    if not login():
        return
    
    ids = extract_ids(get_request(url))
    if not ids:
        return
    datalist = []
    if len(ids) > 5:
        ids = ids[:5]
    for job_id in ids:
        DETAIL_URL = "https://www.shine.com/api/v2/search/candidate/67b86e418a000ae99acedce8/job-description/"
        job_url = DETAIL_URL + job_id
        job_response = session.get(job_url)
        if job_response.status_code == 200:
            try:
                job_data = job_response.json()
                jsn_data = job_data['results']
                for result in jsn_data:
                    obj = {
                        "job_title": clean_text(result.get('jJT', "")),
                        "job_min_exp": clean_text(str(result.get('jExMinId', ""))),
                        "job_industry": clean_text(result.get('jInd', "")),
                        "job_requiter": clean_text(result.get('jRN', "")),
                        "job_active": clean_text(result.get('jAC', "")),
                        "job_requiter_profile": clean_text(result.get('jRUrl', "")),
                        "job_contact_detail": clean_text(str(result.get('jCD', "").replace('\n', '').replace('\r', ''))),
                        "job_qualification": clean_text(result.get('jQA', "")),
                        "job_company_name": clean_text(result.get('jCName', "")),
                        "job_description": clean_text(result.get('jJD', "").replace('\n', '').replace('\r', '')),
                        "job_loc": [clean_text(loc) for loc in result.get('jLoc', [])],
                        "job_post_date": clean_text(str(result.get('jPDate', ""))),
                        "job_keyword": clean_text(result.get('jKwd', "")),
                        "job_exp": clean_text(str(result.get('jExp', ""))),
                        "job_expiry_date": clean_text(str(result.get('jExpDate', "")))
                    }
                    if obj:
                        datalist.append(obj)
                    
            except json.JSONDecodeError:
                pass
        else:
            pass

    return datalist if datalist else None

def scrape_data(location, **kwargs):
    location = location.strip().replace(" ", "-").lower()
    position = kwargs.get('position', "").strip().replace(" ", "-").lower()
    SCRAPE_URL = f"https://www.shine.com/job-search/{position}-jobs-in-{location}"
    data = extract_data(SCRAPE_URL)
    if data:
        return data
    return None

def main(location, **kwargs):
    data = scrape_data(location, **kwargs)
    return data