import requests
import csv
import os

# Basic Configuration
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books_filtered.csv")
BASE_URL = "https://openlibrary.org/search.json"

def fetch_books(query, target_count=50):
    """Simple fetch logic from OpenLibrary"""
    current_page = 1
    books = []
    
    print(f"Connecting to OpenLibrary for: {query}...")

    while len(books) < target_count:
        params = {
            "q": query,
            "page": current_page,
            "limit": 100
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            docs = data.get("docs", [])

            if not docs: break

            for doc in docs:
                books.append({
                    "title": doc.get("title", "N/A"),
                    "author": ", ".join(doc.get("author_name", [])) if doc.get("author_name") else "Unknown",
                    "year": doc.get("first_publish_year", "N/A")
                })
                if len(books) >= target_count: break
            
            current_page += 1
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return books

if __name__ == "__main__":
    results = fetch_books("programming", 50)
    if results:
        if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "author", "year"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Done! Saved 50 books.")