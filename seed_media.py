import os
from dotenv import load_dotenv
from supabase import create_client
from media_config import MEDIA_TO_TRACK

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


def seed_media():
    """Insert media từ media_config.py vào database"""
    # Xóa tất cả media cũ trước
    print("🗑️ Xóa dữ liệu cũ...")
    supabase.table("media").delete().neq("id", 0).execute()
    
    print("\n📥 Thêm media mới...\n")
    
    for media in MEDIA_TO_TRACK:
        data = {
            "anilist_id": media["anilist_id"],
            "title": media["title"],
            "title_english": media.get("title_english", ""),
            "type": media["type"],
            "status": "ONGOING",
            "last_checked": None,
        }

        try:
            response = supabase.table("media").insert(data).execute()
            print(f"✅ {media['title']}")
        except Exception as e:
            print(f"❌ {media['title']}: {e}")
    
    print("\n✨ Hoàn thành!")


if __name__ == "__main__":
    seed_media()