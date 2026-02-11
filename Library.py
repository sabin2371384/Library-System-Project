import requests
import csv
import os
import random

# --- Configurations ---
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books_filtered.csv")
TOPICS_FILE = "topics.txt"

BASE_URL = "https://openlibrary.org/search.json"

def load_topics():
  
    default_topics = ["Programming", "AI", "History", "Science", "Space"]
    if not os.path.exists(TOPICS_FILE):
        with open(TOPICS_FILE, "w") as f:
            f.write("\n".join(default_topics))
        return default_topics
    with open(TOPICS_FILE, "r") as f:
        topics = [line.strip() for line in f if line.strip()]
        return topics if topics else default_topics

def fetch_books(query, target_count=50):
 
    current_page = 1 
    books = []
    
    print(f"\n[Searching for: {query.upper()}]")
    print(f"Fresh Start: Searching from Page 1...")

    while len(books) < target_count:
        params = {
            "q": query,
            "page": current_page,
            "limit": 100,
            "fields": "title,author_name,first_publish_year"
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            docs = data.get("docs", [])

            if not docs:
                print("No more results available.")
                break

            for doc in docs:
                year = doc.get("first_publish_year")
                if year and int(year) > 2000:
                    books.append({
                        "title": doc.get("title", "N/A"),
                        "author": ", ".join(doc.get("author_name", [])) if doc.get("author_name") else "Unknown",
                        "year": year
                    })
                if len(books) >= target_count:
                    break
            
            print(f"-> Page {current_page}: Found {len(books)} total books...")
            current_page += 1 
                
        except Exception as e:
            print(f"Connection Error: {e}")
            break
            
    return books[:target_count]

def main():
    topics = load_topics()
    
    print("====================================")
    print("      LIBRARY DISCOVERY SYSTEM      ")
    print("====================================")
    print("Available Topics:")
    for i, t in enumerate(topics, 1):
        print(f"{i}. {t}")
    
    choice = input("\nSelect a number, type a topic, or press Enter for RANDOM: ").strip()
    
    if not choice:
        selected_query = random.choice(topics)
    elif choice.isdigit() and 0 < int(choice) <= len(topics):
        selected_query = topics[int(choice) - 1]
    else:
        selected_query = choice

    results = fetch_books(selected_query, 50)
    
    if results:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "author", "year"])
            writer.writeheader()
            writer.writerows(results)
            
        print("\n" + "="*40)
        print(f"SUCCESS: 50 fresh books about '{selected_query}' saved.")
        print(f"All previous data in CSV has been replaced.")
        print("="*40)

if name == "main":
    main()