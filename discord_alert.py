import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

print(f"[DEBUG] Discord Webhook URL: {DISCORD_WEBHOOK_URL[:50]}..." if DISCORD_WEBHOOK_URL else "[DEBUG] No Discord URL")


def send_discord_alert(title: str, message: str, color: int = 0x5865F2):
    """Gửi thông báo tới Discord dùng Embed"""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️  Discord Webhook không cấu hình, skip alert")
        return

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

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"✅ Discord alert sent")
        else:
            print(f"❌ Discord error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Discord error: {e}")


def alert_crawler_start():
    """Thông báo crawler bắt đầu"""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_discord_alert(
        "🚀 Anime Tracker - Crawler Started",
        f"⏱️ Bắt đầu cào dữ liệu lúc: {now}",
        color=0xFFA500  # Orange
    )


def alert_crawler_finished(total_count: int, changed_count: int, duration: float):
    """Thông báo crawler kết thúc thành công"""
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
        color=0x57F287  # Green
    )


def alert_crawler_error(error: str):
    """Thông báo lỗi crawler"""
    send_discord_alert(
        "⚠️ Anime Tracker - Crawler Error",
        f"❌ **Lỗi:**\n```\n{error}\n```",
        color=0xED4245  # Red
    )