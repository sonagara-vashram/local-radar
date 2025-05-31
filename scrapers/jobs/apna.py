import json
import random
import re
import requests
from bs4 import BeautifulSoup

def get_headers():
    """Generate random headers for the request."""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

def get_request(url):
    """Fetch HTML content from the given URL with error handling."""
    try:
        response = requests.get(url, headers=get_headers(), timeout=20)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        return None

def extract_urls(data):
    data = json.loads(data)
    jobs = data['results']['jobs']
    urls = []
    for job in jobs:
        url = job['public_url']
        urls.append(url)
    return urls

def clean_text(text):
    if text:
        text = re.sub(r'<.*?>', '', text)  
        text = re.sub(r'[^\w\s@.,&-]', '', text) 
        return text.strip()
    return text

def extract_data(url):    
    datalist = []
    response = get_request(url)
    if response:
        soup = BeautifulSoup(response, 'lxml')
        if soup:
            script = soup.find('p').text
            urls = extract_urls(script)
            if len(urls) >= 5:
                urls = urls[:2]
            for url in urls:
                if url:
                    res = get_request(url)
                    if res:
                        soup = BeautifulSoup(res, 'lxml')
                        script = soup.find('script', id="__NEXT_DATA__")
                        data = script.string
                        json_data = json.loads(data)
                        job = json_data['props']['pageProps']['job']
                        obj = {}
                        obj["title"] = clean_text(job.get("title", "").strip().replace('\n', '').replace('\r', ''))
                        obj["description"] = clean_text(job.get("description", "").strip().replace('\n', '').replace('\r', ''))
                        obj["created_on"] = job.get("created_on", "")
                        obj["expiry"] = job.get("expiry", "")
                        obj["experience_required"] = job.get("experience_in_years", "")
                        obj["no_of_openings"] = job.get("no_of_openings", "")
                        obj["category_slug"] = job.get("category_slug", "")
                        obj["area_slug"] = job.get("area_slug", "")
                        obj["city_slug"] = job.get("city_slug", "")
                        
                        obj["employment_type"] = job.get("employment_type", "")
                        obj["education"] = job.get("education", "")
                        obj["english"] = job.get("english", "")
                        obj["shift"] = job.get("shift", "")
                        obj["skills_required"] = job.get("skills_required", [])
                        
                        # Salary Details
                        obj["salary"] = {
                            "min_salary": job.get("min_salary", ""),
                            "max_salary": job.get("max_salary", ""),
                        }
                        
                        # Organization Details
                        organization = job.get("organization", {})
                        obj["organization"] = {
                            "name": organization.get("name", ""),
                        }
                        
                        # Address Details (Primary)
                        address = job.get("address", {})
                        city_info = address.get("city", {})
                        obj["address"] = {
                            "address1": address.get("line_1", ""),
                            "area": address.get("area", ""),
                            "city": city_info.get("name", "")
                        }
                        
                        # Alternate Address
                        address_v2 = job.get("address_v2", {})
                        if address_v2:
                            obj["address_v2"] = {
                                "address2": address_v2.get("line_1", ""),
                                "area": address_v2.get("area", ""),
                                "latitude": address_v2.get("latitude", ""),
                                "longitude": address_v2.get("longitude", ""),
                                "city": address_v2.get("city", {}).get("name", "")
                            }
                        else:
                            obj["address_v2"] = {}
                        
                        # Job Highlights
                        job_highlights = job.get("job_highlights", [])
                        obj["job_highlights"] = []
                        for highlight in job_highlights:
                            obj["job_highlights"].append({
                                "heading": highlight.get("heading", ""),
                                "description": highlight.get("description", ""),
                            })
                                                
                        # Company Address
                        company_address = job.get("company_address", {})
                        if company_address:
                            area_info = company_address.get("area", {})
                            city_detail = area_info.get("city", {}) if isinstance(area_info, dict) else {}
                            obj["company_address"] = {
                                "company_address": company_address.get("line_1", ""),
                                "area": area_info.get("name", ""),
                                "city": city_detail.get("name", "")
                            }
                        else:
                            obj["company_address"] = {}
                        
                        # Interview Details
                        obj["interview_details"] = {}
                        obj["interview_details"]['type'] = job.get("interview_details", {}).get("type", "")
                        obj["interview_details"]['heading'] = job.get("interview_details", {}).get("heading", "")
                        data_ = [] 
                        interview_data = job.get("interview_details", {}).get("data", [])
                        for data in interview_data:
                            data_.append({
                                "heading": data.get("heading", ""),
                                "sub_heading": data.get("sub_heading", ""),
                            })
                        obj["interview_details"]['data'] = data_
                            
                        # Additional Descriptions
                        obj["rich_description"] = clean_text(job.get("rich_description", "").strip().replace('\n', '').replace('\r', ''))   
                        obj["jobDescriptionTemplate"] = clean_text(job.get("jobDescriptionTemplate", "").strip().replace('\n', '').replace('\r', ''))
                        obj["jobDescription"] = clean_text(job.get("jobDescription", "").strip().replace('\n', '').replace('\r', ''))
                        obj["shortJobDescription"] = clean_text(job.get("shortJobDescription", "").strip().replace('\n', '').replace('\r', ''))
                        
                        # Public URLs
                        obj["public_url"] = job.get("public_url", "")
                        
                        # Degree Requirements
                        obj["degree_requirements"] = job.get("degree_requirements", "")
                        
                        datalist.append(obj)
    return datalist if datalist else None

def scrape_data(location, **kwargs):
    location = location.replace(' ', '+').lower()
    position = kwargs.get('position', '').replace(' ', '+').lower()
    url = f'https://production.apna.co/user-profile-orchestrator/public/v1/jobs/?location_name={location}&search=true&text={position}&posted_in=72'
    data = extract_data(url)
    if data:
        return data
    
def main(location, **kwargs):
    return scrape_data(location, **kwargs)