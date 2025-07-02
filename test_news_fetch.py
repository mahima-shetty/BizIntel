import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load your .env file

topic = "AI"
api_key = os.getenv("NEWS_API_KEY")  # replace with your actual env var name

url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=3&apiKey={api_key}"

response = requests.get(url)
print("Status Code:", response.status_code)
print("Response JSON:")

data = response.json()
print(data)

# Optional: print only titles
for article in data.get("articles", []):
    print("-", article["title"])
