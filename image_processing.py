import cv2
import base64
import requests
from serpapi.google_search import GoogleSearch
from typing import Dict, List
from config import IMGBB_API_KEY, SERPAPI_API_KEY

def upload_image_to_imgbb(image_data):
    """Upload an image to ImgBB and return the URL"""
    is_success, buffer = cv2.imencode(".jpg", image_data)
    if not is_success:
        return None
    
    image_b64 = base64.b64encode(buffer).decode("utf-8")
    
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": image_b64
        }
    )
    
    if response.status_code != 200:
        return None
        
    result = response.json()
    if not result.get("success", False):
        return None
        
    return result["data"]["url"]

def extract_urls_from_serpapi(results: Dict) -> List[str]:
    """Extract URLs from SerpAPI Google Reverse Image search results"""
    urls = []
    
    # Check for different results sections and extract URLs
    sections_to_check = {
        "image_results": "link",
        "inline_images": "source",
        "visual_matches": "link", 
        "pages_with_matching_images": "url",
        "organic_results": "link"
    }
    
    for section_name, link_key in sections_to_check.items():
        if section_name in results and isinstance(results[section_name], list):
            for item in results[section_name]:
                if link_key in item and item[link_key] not in urls:
                    urls.append(item[link_key])
    
    return urls

def find_websites_from_image(image_url):
    """Search for websites using reverse image search"""
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google_reverse_image",
        "image_url": image_url,
        "location": "United States",
        "hl": "en",
        "gl": "us"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    return extract_urls_from_serpapi(results)[:5]  # Limit to 5 URLs 