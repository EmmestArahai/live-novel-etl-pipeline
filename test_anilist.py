import requests
import json

ANILIST_API = "https://graphql.anilist.co"

# GraphQL query lấy thông tin anime/manga
QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    id
    title {
      romaji
      english
      native
    }
    coverImage {
      large
    }
    description
    status
    episodes
    chapters
    averageScore
    meanScore
    popularity
    trending
    genres
    startDate {
      year
      month
      day
    }
  }
}
"""

def search_media(title, media_type="ANIME"):
    """Search anime/manga trên AniList"""
    variables = {
        "search": title
    }
    
    # Sửa query để dùng ANIME hoặc MANGA
    query = QUERY.replace("type: ANIME", f"type: {media_type}")
    
    response = requests.post(
        ANILIST_API,
        json={"query": query, "variables": variables},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]["Media"]:
            return data["data"]["Media"]
    
    return None


def main():
    # Test: tìm 1 anime nổi tiếng
    test_titles = [
        "Attack on Titan",
        "Demon Slayer",
        "Solo Leveling",
        "That Time I Got Reincarnated as a Slime"
    ]
    
    for title in test_titles:
        print(f"\n=== Searching: {title} ===")
        result = search_media(title, "ANIME")
        
        if result:
            print(f"Title: {result['title']['romaji']}")
            print(f"Status: {result['status']}")
            print(f"Episodes: {result['episodes']}")
            print(f"Score: {result['averageScore']}/100")
            print(f"Popularity: {result['popularity']}")
        else:
            print("Not found")


if __name__ == "__main__":
    main()