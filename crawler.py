import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from media_config import MEDIA_TO_TRACK
from discord_alert import alert_crawler_start, alert_crawler_finished, alert_crawler_error
import time

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

ANILIST_API = "https://graphql.anilist.co"

# GraphQL query lấy data media
MEDIA_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    title {
      romaji
      english
    }
    coverImage {
      large
    }
    description
    status
    episodes
    chapters
    averageScore
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

def fetch_media_from_anilist(anilist_id):
    """Lấy data từ AniList bằng ID"""
    variables = {"id": anilist_id}
    
    try:
        response = requests.post(
            ANILIST_API,
            json={"query": MEDIA_QUERY, "variables": variables},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]["Media"]:
                return data["data"]["Media"]
    except Exception as e:
        print(f"❌ Lỗi fetch AniList (ID {anilist_id}): {e}")
    
    return None


def update_media_in_db(media_id, anilist_data):
    """
    Cập nhật media trong DB + tạo history record
    
    Args:
        media_id: ID trong DB (supabase)
        anilist_data: data từ AniList API
    
    Returns:
        dict: {'updated': bool, 'changes': dict}
    """
    if not anilist_data:
        return {"updated": False, "changes": {}}
    
    # Lấy data cũ từ DB để so sánh
    old_data = supabase.table("media").select(
        "episodes, chapters, average_score"
    ).eq("id", media_id).execute()
    
    if not old_data.data:
        return {"updated": False, "changes": {}}
    
    old = old_data.data[0]
    
    # Chuẩn bị data mới
    new_data = {
        "episodes": anilist_data.get("episodes"),
        "chapters": anilist_data.get("chapters"),
        "average_score": anilist_data.get("averageScore"),
        "popularity": anilist_data.get("popularity"),
        "trending": anilist_data.get("trending"),
        "status": anilist_data.get("status"),
        "genres": anilist_data.get("genres"),
        "last_checked": datetime.utcnow().isoformat()
    }
    
    # Phát hiện thay đổi
    changes = {}
    if old.get("episodes") != new_data.get("episodes"):
        changes["episodes"] = {
            "before": old.get("episodes"),
            "after": new_data.get("episodes")
        }
    if old.get("chapters") != new_data.get("chapters"):
        changes["chapters"] = {
            "before": old.get("chapters"),
            "after": new_data.get("chapters")
        }
    if old.get("average_score") != new_data.get("average_score"):
        changes["average_score"] = {
            "before": old.get("average_score"),
            "after": new_data.get("average_score")
        }
    
    # Update media table
    supabase.table("media").update(new_data).eq("id", media_id).execute()
    
    # Insert history record (dù có thay đổi hay không)
    history_record = {
        "media_id": media_id,
        "episodes_before": old.get("episodes"),
        "episodes_after": new_data.get("episodes"),
        "chapters_before": old.get("chapters"),
        "chapters_after": new_data.get("chapters"),
        "score_before": old.get("average_score"),
        "score_after": new_data.get("average_score"),
        "changes_detected": len(changes) > 0
    }
    supabase.table("media_history").insert(history_record).execute()
    
    return {
        "updated": True,
        "changes": changes
    }


def run_crawler():
    """Main crawler"""
    start_time = time.time()
    
    print("\n🚀 Bắt đầu crawler...\n")
    
    # ⭐ Thêm print debug
    print("[DEBUG] Calling alert_crawler_start()...")
    try:
        alert_crawler_start()
        print("[DEBUG] alert_crawler_start() completed")
    except Exception as e:
        print(f"[DEBUG] ERROR in alert_crawler_start(): {e}")
    
    try:
        # Lấy danh sách media cần update
        media_list = supabase.table("media").select("id, anilist_id, title").execute()
        
        if not media_list.data:
            print("❌ Không có media nào trong DB")
            alert_crawler_error("Không có media nào trong DB")
            return
        
        total = len(media_list.data)
        updated_count = 0
        changed_count = 0
        
        for idx, media in enumerate(media_list.data, 1):
            print(f"[{idx}/{total}] Crawling: {media['title']} (AniList ID: {media['anilist_id']})")
            
            anilist_data = fetch_media_from_anilist(media["anilist_id"])
            
            if anilist_data:
                result = update_media_in_db(media["id"], anilist_data)
                
                if result["updated"]:
                    updated_count += 1
                    if result["changes"]:
                        changed_count += 1
                        print(f"  ✅ Cập nhật: {result['changes']}")
                    else:
                        print(f"  ✓ Không có thay đổi")
            else:
                print(f"  ⚠️  Fetch AniList thất bại")
            
            time.sleep(1)
        
        duration = time.time() - start_time
        
        print(f"\n📊 Kết quả:")
        print(f"  - Tổng media: {total}")
        print(f"  - Cập nhật thành công: {updated_count}")
        print(f"  - Có thay đổi: {changed_count}")
        print(f"  - Thời gian: {duration:.1f}s")
        
        # ⭐ Thêm print debug
        print("[DEBUG] Calling alert_crawler_finished()...")
        try:
            alert_crawler_finished(total, changed_count, duration)
            print("[DEBUG] alert_crawler_finished() completed")
        except Exception as e:
            print(f"[DEBUG] ERROR in alert_crawler_finished(): {e}")
        
    except Exception as e:
        print(f"\n❌ Lỗi crawler: {e}")
        print("[DEBUG] Calling alert_crawler_error()...")
        try:
            alert_crawler_error(str(e))
            print("[DEBUG] alert_crawler_error() completed")
        except Exception as alert_e:
            print(f"[DEBUG] ERROR in alert_crawler_error(): {alert_e}")
        raise

if __name__ == "__main__":
    run_crawler()