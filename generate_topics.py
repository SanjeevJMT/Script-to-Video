import requests
import os

# Configuration
API_KEY = "YOUR_API_KEY"  # Replace with your Groq API key
NICHE = input("Enter your niche (e.g., 'DIY', 'Fitness', 'Tech', etc.): ")
TOPICS_FILE = "topics.txt"

def generate_topics(niche, api_key):
    """
    Generate 100 interesting topic ideas for a given niche using Groq API.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    prompt = f"Generate 5 interesting, unique, and engaging topic ideas for viral video content in the {niche} niche. Each topic should be catchy, trending, and suitable for a broad audience. Make sure topics are diverse and cover various sub-topics within the {niche} niche."

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Failed to generate topics. Check your API key and try again.")
        return None

def save_topics_to_file(topics, filename):
    """
    Save topics to a text file, one per line.
    """
    with open(filename, 'w') as f:
        f.write(topics)

    print(f"Topics saved to: {os.path.abspath(filename)}")

def main():
    print(f"Generating 100 topics for niche: {NICHE}")
    topics_response = generate_topics(NICHE, api_key)

    if topics_response:
        # Split the response into individual topics
        topics_list = topics_response.split('\n')

        # Remove any empty lines or duplicates
        unique_topics = list(dict.fromkeys([topic.strip() for topic in topics_list if topic.strip() != '']))

        # Ensure we have at least 100 topics
        if len(unique_topics) >= 100:
            final_topics = '\n'.join(unique_topics[:100])
            save_topics_to_file(final_topics, TOPICS_FILE)
        else:
            print("Not enough topics generated. count ="+ str(len(unique_topics)) )
            final_topics = '\n'.join(unique_topics[:100])
            save_topics_to_file(final_topics, TOPICS_FILE)
    else:
        print("Failed to generate topics.")

if __name__ == "__main__":
    main()