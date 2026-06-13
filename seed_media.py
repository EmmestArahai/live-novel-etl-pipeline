import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Danh sách anime/manga mẫu (bạn có thể sửa)
MEDIA_TO_TRACK = [
    {
        "anilist_id": 16498,  # Attack on Titan (Shingeki no Kyojin)
        "title": "Shingeki no Kyojin",
        "title_english": "Attack on Titan",
        "type": "ANIME",
        "status": "FINISHED",
        "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-LI8GE46A6CZw.jpg",
        "episodes": 139,
        "average_score": 85,
        "popularity": 1010734,
        "genres": ["Action", "Drama", "Fantasy"]
    },
    {
        "anilist_id": 113415,  # Solo Leveling
        "title": "Ore dake Level Up na Ken",
        "title_english": "Solo Leveling",
        "type": "ANIME",
        "status": "FINISHED",
        "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx113415-wCB6RR1kPfSR.jpg",
        "episodes": 12,
        "average_score": 81,
        "popularity": 414682,
        "genres": ["Action", "Adventure", "Fantasy"]
    },
    {
        "anilist_id": 101573,  # That Time I Got Reincarnated as a Slime
        "title": "Tensei Shitara Slime Datta Ken",
        "title_english": "That Time I Got Reincarnated as a Slime",
        "type": "ANIME",
        "status": "FINISHED",
        "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101573-H0sptC7ySp4O.jpg",
        "episodes": 24,
        "average_score": 80,
        "popularity": 438606,
        "genres": ["Adventure", "Comedy", "Fantasy"]
    }
]

def seed_media():
    """Insert media vào database"""
    for media in MEDIA_TO_TRACK:
        # Kiểm tra đã tồn tại chưa
        existing = supabase.table("media").select("id").eq(
            "anilist_id", media["anilist_id"]
        ).execute()
        
        if existing.data:
            print(f"⏭️  {media['title']} đã tồn tại, skip")
            continue
        
        # Insert
        response = supabase.table("media").insert(media).execute()
        if response.data:
            print(f"✅ Thêm: {media['title']}")
        else:
            print(f"❌ Lỗi: {media['title']}")


if __name__ == "__main__":
    seed_media()