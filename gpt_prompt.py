import openai
from config import OPENAI_API_KEY

def openai_prompt(text):
    """Generate socializing tips from scraped content using OpenAI"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"""
You are given text extracted from a website discovered via a reverse image search of a person's face:

{text}

Your task:
1. Determine whether this text is about a specific real person. If it is not, clearly state that the content is unrelated and return this exact format:

Name: Unknown  
Overview: No identifiable personal information found.  
Tips for socializing with this person:
- Be friendly
- Ask general questions
- Use open body language
- Show interest
- Smile often

2. If it contains information about a specific individual, extract:
- Name (if available)
- A 1–2 sentence overview describing who they are (profession, notable info, interests)
- 4–5 short, personalized socializing tips (max 30 characters each). 
  Each tip should be an **actionable command** (e.g., "Mention machine learning").

Format your output exactly like this:

Name: [person's name or "Unknown"]  
Overview: [brief description or "No identifiable personal information found."]  
Tips for socializing with this person:
- [Tip 1]
- [Tip 2]
- [Tip 3]
- [Tip 4]
- [Tip 5]
"""
        }]
    )
    
    return response.choices[0].message.content.strip() 