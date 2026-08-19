
import requests
import time
import json
import os
from datetime import datetime


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

HEADERS = {
    "User-Agent": "TrendPulse/1.0"
}


CATEGORIES = {
    "technology": [
        "ai", "software", "tech", "code", "computer",
        "data", "cloud", "api", "gpu", "llm"
    ],

    "worldnews": [
        "war", "government", "country", "president",
        "election", "climate", "attack", "global"
    ],

    "sports": [
        "nfl", "nba", "fifa", "sport", "game", "team",
        "player", "league", "championship"
    ],

    "science": [
        "research", "study", "space", "physics", "biology",
        "discovery", "nasa", "genome"
    ],

    "entertainment": [
        "movie", "film", "music", "netflix", "game",
        "book", "show", "award", "streaming"
    ]
}


def get_category(title):
    """
    Check whether the title contains a keyword
    from any of the five categories.
    Matching is case-insensitive.
    """

    title_lower = title.lower()

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category

    return None


def main():

    # Fetch the list of top 500 HackerNews story IDs
    try:
        response = requests.get(
            TOP_STORIES_URL,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        story_ids = response.json()[:500]

        print(f"Fetched {len(story_ids)} top story IDs.")

    except requests.RequestException as error:
        print(f"Failed to fetch top story IDs: {error}")
        return


    # Store stories separately for each category
    stories_by_category = {
        category: []
        for category in CATEGORIES
    }


    # Fetch details of each story
    for story_id in story_ids:

        # Stop when every category has 25 stories
        if all(
            len(stories_by_category[category]) >= 25
            for category in CATEGORIES
        ):
            break

        try:
            response = requests.get(
                ITEM_URL.format(story_id),
                headers=HEADERS,
                timeout=10
            )

            response.raise_for_status()

            story = response.json()

        except requests.RequestException as error:
            print(f"Failed to fetch story {story_id}: {error}")
            continue


        # Skip missing or invalid stories
        if not story:
            continue

        title = story.get("title")

        if not title:
            continue


        # Find the category from the title
        category = get_category(title)

        if category is None:
            continue


        # Maximum 25 stories per category
        if len(stories_by_category[category]) >= 25:
            continue


        # Create the seven required fields
        collected_story = {
            "post_id": story.get("id"),
            "title": title,
            "category": category,
            "score": story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author": story.get("by"),
            "collected_at": datetime.now().isoformat()
        }


        stories_by_category[category].append(collected_story)

        print(
            f"{category}: "
            f"{len(stories_by_category[category])}/25"
        )


    # Combine all categories
    all_stories = []

    for category in CATEGORIES:

        all_stories.extend(
            stories_by_category[category]
        )

        # Required delay between category loops
        time.sleep(2)


    # Create data folder
    os.makedirs("data", exist_ok=True)


    # Create today's filename
    date_string = datetime.now().strftime("%Y%m%d")

    filename = f"data/trends_{date_string}.json"


    # Save stories to JSON
    with open(filename, "w", encoding="utf-8") as file:

        json.dump(
            all_stories,
            file,
            indent=4,
            ensure_ascii=False
        )


    print()
    print(f"Collected {len(all_stories)} stories.")
    print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
