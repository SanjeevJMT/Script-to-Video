import requests
import pandas as pd
import os
import time

# Configuration
API_KEY = ""  # Replace with your Groq API key
TOPICS_FILE = "topics.txt"  # File containing 100 topics (one per line)
OUTPUT_EXCEL = "viral_scripts.xlsx"

def get_groq_script(prompt, api_key):
    """
    Generate a 140-word script using Groq API.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "user",
                "content": f"Create about 140-word story script withoud any double inverted commas as Narrated by someone for a viral video about: {prompt}. The Narration should be complete-sentenced , informative , engaging, catchy. you should only return the Narrated story and Not start with Topic, Also include a call to action at the end with thanks note for watching and requesting for subscribing."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        #print(response.json()["choices"][0]["message"]["content"])
        return response.json()["choices"][0]["message"]["content"]
    else:
        return None

def main():
    # Read topics from file
    with open(TOPICS_FILE, 'r') as f:
        topics = [line.strip() for line in f.readlines()]

    # Generate scripts
    data = []
    for topic in topics:
        print(f"Generating script for: {topic}")
        script = get_groq_script(topic, API_KEY)
        if script:
            data.append({"Topic": topic, "Script": script})
        else:
            print(f"Failed to generate script for: {topic}")
        # Add a 3-second wait between API calls
        time.sleep(3)
    # Create DataFrame and save to Excel
    df = pd.DataFrame(data)
    df.to_excel(OUTPUT_EXCEL, index=False)
    print("Scripts generated and saved to:", OUTPUT_EXCEL)

if __name__ == "__main__":
    main()