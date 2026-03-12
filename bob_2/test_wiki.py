import os
import urllib.request
import json
import urllib.parse
from google import genai
from google.genai import types

def get_wikipedia_image(query: str) -> str:
    """Finds an image URL from Wikipedia for the given query."""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'SteveAgent/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("query", {}).get("search"):
                title = data["query"]["search"][0]["title"]
                img_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(title)}"
                req2 = urllib.request.Request(img_url, headers={'User-Agent': 'SteveAgent/1.0'})
                with urllib.request.urlopen(req2) as resp2:
                    data2 = json.loads(resp2.read().decode())
                    pages = data2.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        if "original" in page_data:
                            return page_data["original"]["source"]
    except Exception as e:
        return f"Error: {e}"
    return "No image found."


client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Can you show me a picture of NGC 5134 using the image tool?',
    config=types.GenerateContentConfig(
        tools=[get_wikipedia_image],
        temperature=0.1
    )
)

print(response.text)
