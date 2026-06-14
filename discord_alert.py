import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

print(f"[DEBUG] Discord URL loaded: {'Yes' if DISCORD_WEBHOOK_URL else 'No'}")


def send_discord_alert(title: str, message: str, color: int = 0x5865F2, retries: int = 3):
    """Gửi thông báo tới Discord với retry"""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️  Discord Webhook không cấu hình")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    for attempt in range(retries):
        try:
            print(f"[DEBUG] Gửi Discord message (attempt {attempt + 1}/{retries})...")
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            
            print(f"[DEBUG] Discord response status: {response.status_code}")
            
            if response.status_code == 204:
                print(f"✅ Discord alert sent successfully")
                return True
            else:
                print(f"⚠️  Discord error {response.status_code}: {response.text}")
                if attempt < retries - 1:
                    print(f"Retry sau 2 giây...")
                    time.sleep(2)
        except Exception as e:
            print(f"❌ Discord error: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    
    return False


def alert_crawler_start():
    """Thông báo crawler bắt đầu"""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_discord_alert(
        "🚀 Anime Tracker - Crawler Started",
        f"⏱️ Bắt đầu cào dữ liệu lúc: {now}",
        color=0xFFA500
    )


def alert_crawler_finished(total_count: int, changed_count: int, duration: float):
    """Thông báo crawler kết thúc"""
    message = f"""
📊 **Kết quả:**
- Tổng media theo dõi: **{total_count}**
- Có thay đổi: **{changed_count}**
- Thời gian: **{duration:.1f}s**

✨ Sẽ cập nhật vào ngày hôm sau!
    """.strip()

    send_discord_alert(
        "✅ Anime Tracker - Crawler Finished",
        message,
        color=0x57F287
    )


def alert_crawler_error(error: str):
    """Thông báo lỗi crawler"""
    send_discord_alert(
        "⚠️ Anime Tracker - Crawler Error",
        f"❌ **Lỗi:**\n```\n{error}\n```",
        color=0xED4245
    )