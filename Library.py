import requests
import csv
import os
import random
from typing import List, Dict, Optional

# --- Configurations ---
OUTPUT_DIR: str = "output"
OUTPUT_FILE: str = os.path.join(OUTPUT_DIR, "books_filtered.csv")
TOPICS_FILE: str = "topics.txt"

BASE_URL: str = "https://openlibrary.org/search.json"


def load_topics() -> List[str]:
    """
    Load topics from topics.txt or create default ones.
    """
    default_topics: List[str] = ["Programming", "AI", "History", "Science", "Space"]
    if not os.path.exists(TOPICS_FILE):
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(default_topics))
        return default_topics
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics: List[str] = [line.strip() for line in f if line.strip()]
        return topics if topics else default_topics


def fetch_books(query: str, target_count: int = 50) -> List[Dict[str, str | int]]:
    """
    Fetch books from OpenLibrary API based on a query.
    Returns a list of dictionaries with 'title', 'author', and 'year'.
    """
    current_page: int = 1
    books: List[Dict[str, str | int]] = []

    print(f"\n[Searching for: {query.upper()}]")
    print(f"Fresh Start: Searching from Page 1...")

    while len(books) < target_count:
        params: Dict[str, str | int] = {
            "q": query,
            "page": current_page,
            "limit": 100,
            "fields": "title,author_name,first_publish_year"
        }

        try:
            response: requests.Response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data: Dict = response.json()
            docs: List[Dict] = data.get("docs", [])

            if not docs:
                print("No more results available.")
                break

            for doc in docs:
                year: Optional[int] = doc.get("first_publish_year")
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


def main() -> None:
    topics: List[str] = load_topics()

    print("====================================")
    print("      LIBRARY DISCOVERY SYSTEM      ")
    print("====================================")
    print("Available Topics:")
    for i, t in enumerate(topics, 1):
        print(f"{i}. {t}")

    choice: str = input("\nSelect a number, type a topic, or press Enter for RANDOM: ").strip()

    if not choice:
        selected_query: str = random.choice(topics)
    elif choice.isdigit() and 0 < int(choice) <= len(topics):
        selected_query: str = topics[int(choice) - 1]
    else:
        selected_query: str = choice

    results: List[Dict[str, str | int]] = fetch_books(selected_query, 50)

    if results:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer: csv.DictWriter = csv.DictWriter(f, fieldnames=["title", "author", "year"])
            writer.writeheader()
            writer.writerows(results)

        print("\n" + "="*40)
        print(f"SUCCESS: {len(results)} fresh books about '{selected_query}' saved.")
        print(f"All previous data in CSV has been replaced.")
        print("="*40)


if __name__ == "__main__":
    main()
