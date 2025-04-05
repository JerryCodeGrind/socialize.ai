import threading
import json
from image_processing import upload_image_to_imgbb, find_websites_from_image
from web_scraping import scrape_website_content
from gpt_prompt import openai_prompt

def search_face_in_background(face_img, callback):
    """Process face image with reverse search in a background thread"""
    try:
        # Upload to ImgBB
        callback(status="Uploading and searching...")
        image_url = upload_image_to_imgbb(face_img)
        if not image_url:
            callback(status="Failed to upload image.")
            callback(search_complete=True)
            return
        
        # Find websites
        urls = find_websites_from_image(image_url)
        
        # No URLs found
        if not urls:
            # Return a default result when no sites are found
            default_result = [{
                "title": "No Results",
                "link": "#",
                "snippet": """
Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often
"""
            }]
            callback(status="No websites found", results=default_result)
            callback(search_complete=True)
            return
        
        # Process each URL
        results = []
        for url in urls:
            # Create basic result entry
            result = {
                "title": url.split('//')[-1].split('/')[0],
                "link": url
            }
            
            # Scrape content
            content = scrape_website_content(url)
            
            # Generate summary with OpenAI if we have content
            if content and len(content) > 100:
                try:
                    # The openai_prompt function now handles its own errors
                    socialization_tips = openai_prompt(content)
                    result["snippet"] = socialization_tips
                    
                    # Print to console for debugging
                    print("\n" + "-"*50)
                    print(f"URL: {url}")
                    print(socialization_tips)
                    print("-"*50 + "\n")
                except Exception as e:
                    # This shouldn't happen now, but just in case
                    print(f"Error in search process: {str(e)}")
                    result["snippet"] = """
Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often
"""
            else:
                # Not enough content, use default
                result["snippet"] = """
Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often
"""
            
            results.append(result)
        
        # Save results
        with open("search_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Update callback with results
        if results:
            callback(status="Search complete", results=results)
        else:
            default_result = [{
                "title": "No Results",
                "link": "#",
                "snippet": """
Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often
"""
            }]
            callback(status="No useful information found", results=default_result)
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        # Return default result on error
        default_result = [{
            "title": "Error",
            "link": "#",
            "snippet": """
Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often
"""
        }]
        callback(status="Search error", results=default_result)
    
    callback(search_complete=True) 