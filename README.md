# 🎬 Live Novel ETL Pipeline - Anime Tracker

**Hệ thống tự động cập nhật dữ liệu anime/manga từ AniList mỗi ngày, lưu vào Supabase, và gửi thông báo qua Discord.**

---

## 📋 Mục tiêu dự án

- ✅ **Extract**: Crawl data anime/manga từ AniList API
- ✅ **Transform**: So sánh dữ liệu cũ/mới, phát hiện thay đổi
- ✅ **Load**: Lưu vào Supabase PostgreSQL (Free tier)
- ✅ **Automate**: Chạy tự động mỗi ngày 00:00 UTC qua GitHub Actions
- ✅ **Alert**: Gửi thông báo kết quả qua Discord Webhook

---

## 🛠️ Tech Stack

| Thành phần | Công nghệ |
|-----------|----------|
| **Language** | Python 3.11+ |
| **Web Scraping** | requests + AniList GraphQL API |
| **Database** | Supabase (PostgreSQL) - Free tier |
| **Automation** | GitHub Actions (Cron job) |
| **Notifications** | Discord Webhook |
| **AI Assistant** | Claude Free mỗi 5 tiếng vắt một lần, hết quota tuần thì thôi |

---

## 🚀 Quick Start

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/live-novel-etl-pipeline.git
cd live-novel-etl-pipeline
```

### 2️⃣ Cài đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### 3️⃣ Cấu hình Environment

Tạo file `.env` ở root project:

```bash
# Supabase Config
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your_service_role_key_here

# Discord Webhook Config
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Cách lấy credentials:**

#### **Supabase URL + Key**
1. Vào [supabase.com](https://supabase.com) → Project Settings → API
2. Copy **Project URL** và **service_role key**

#### **Discord Webhook URL**
1. Vào Discord server của bạn → #channel muốn nhận alert
2. Channel Settings → Integrations → Webhooks → New Webhook
3. Copy **Webhook URL**

### 4️⃣ Tạo Database Supabase

Vào **SQL Editor** trong Supabase, chạy:

```sql
create table media (
    id bigint generated always as identity primary key,
    anilist_id int unique not null,
    title text not null,
    title_english text,
    type text not null,
    status text,
    cover_image text,
    description text,
    
    episodes int,
    chapters int,
    average_score numeric(5,2),
    popularity int,
    trending int,
    genres text[],
    
    last_checked timestamptz,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index idx_media_anilist_id on media(anilist_id);

create table media_history (
    id bigint generated always as identity primary key,
    media_id bigint references media(id) on delete cascade,
    
    episodes_before int,
    episodes_after int,
    chapters_before int,
    chapters_after int,
    score_before numeric(5,2),
    score_after numeric(5,2),
    
    checked_at timestamptz default now(),
    changes_detected boolean default false
);

create index idx_media_history_media_id on media_history(media_id);
```

---

## 📝 Cách sử dụng

### Thêm/Sửa anime muốn theo dõi

Mở file `media_config.py` và thêm/xóa anime:

```python
MEDIA_TO_TRACK = [
    {
        "anilist_id": 168259,  # ID từ AniList
        "title": "Anime Name",
        "title_english": "English Name",
        "type": "ANIME",  # hoặc "MANGA"
    },
    # ... thêm anime khác
]
```

**Cách tìm Anime List ID chính xác:**

Chạy script để tìm ID:

```bash
python find_anime_id.py
```

Sẽ in ra danh sách anime + ID từ AniList.

### Seed dữ liệu vào Database

```bash
python seed_media.py
```

Output:
📥 Thêm media mới...
✅ Anime 1

✅ Anime 2

...

✨ Hoàn thành!

### Chạy Crawler Local

```bash
python crawler.py
```

Output:
🚀 Bắt đầu crawler...
[1/11] Crawling: Anime 1 (AniList ID: 12345)

✓ Không có thay đổi

[2/11] Crawling: Anime 2 (AniList ID: 67890)

✅ Cập nhật: {'episodes': {'before': 12, 'after': 13}}
📊 Kết quả:
Tổng media: 11
Cập nhật thành công: 11
Có thay đổi: 1
Thời gian: 43.5s

**Đồng thời bạn sẽ nhận 2 Discord messages:**
1. 🚀 Crawler Started
2. ✅ Crawler Finished (với kết quả)

---

## 🔄 Tự động chạy hàng ngày (GitHub Actions)

1. **Push code lên GitHub**:
```bash
   git add .
   git commit -m "Add initial ETL pipeline"
   git push origin main
```

2. **Thêm Secrets trên GitHub**:
   - Vào Repository → Settings → Secrets and variables → Actions
   - Thêm 3 secrets:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `DISCORD_WEBHOOK_URL`

3. **Workflow sẽ tự chạy**:
   - ⏰ **Mỗi ngày lúc 00:00 UTC** (= 07:00 +07:00)
   - 📝 Hoặc chạy manual: Actions tab → ETL Pipeline → Run workflow

---

## 📁 Cấu trúc dự án
live-novel-etl-pipeline/

├── crawler.py                  # Main ETL logic

├── media_config.py             # ⭐ Danh sách anime theo dõi

├── discord_alert.py            # Discord notification handler

├── find_anime_id.py            # Tìm ID AniList chính xác

├── seed_media.py               # Seed media vào database

├── requirements.txt            # Python dependencies

├── README.md                   # (file này)

├── .env                        # Local config (DO NOT pushed to GitHub!!!!!!)

├── .gitignore                  # Ignore files

└── .github/workflows/

└── etl.yml                 # GitHub Actions workflow

---

## 🔧 Troubleshooting

### ❌ "Không nhận được Discord message"

**Kiểm tra:**
1. Discord Webhook URL có đúng không?
```bash
   echo $DISCORD_WEBHOOK_URL  # Verify URL
```

2. `.env` file có chứa `DISCORD_WEBHOOK_URL=...`?

3. Chạy test local:
```bash
   python crawler.py
```
   Nếu thấy `✅ Discord alert sent` → OK. Nếu không → check URL.

### ❌ "Fetch AniList thất bại" cho nhiều anime

**Nguyên nhân:** ID AniList sai hoặc anime không tồn tại trên AniList.

**Fix:**
```bash
python find_anime_id.py
```

Copy ID chính xác vào `media_config.py`, rồi:
```bash
python seed_media.py
python crawler.py
```

### ❌ "Supabase connection error"

**Kiểm tra:**
1. URL/Key có đúng không?
2. Supabase project còn hoạt động không?
3. Database tables đã tạo chưa? (chạy SQL ở trên)

---

## 📊 Xem dữ liệu trong Supabase

1. Vào [app.supabase.com](https://app.supabase.com)
2. Chọn project → Table Editor
3. Xem tables:
   - **media**: Danh sách anime + data mới nhất
   - **media_history**: Lịch sử cập nhật từng ngày

---

## 🎯 Dự tính mở rộng (cái này con claude muốn làm, còn tôi thì quá lười để làm theo nó)

- [ ] Thêm hỗ trợ manga
- [ ] Crawl từ các source khác (MyAnimeList, Aniwatch)
- [ ] Web dashboard để quản lý danh sách
- [ ] Email notifications
- [ ] Slack integration

---

## 📝 License

MIT License - Feel free to use for personal projects

---

## 👨‍💻 Author

Created with ❤️ for anime fans who want to stay updated!

---

## 🤝 Contribute

Nếu có ý kiến cải tiến, vui lòng (trong trường hợp tôi lên github check và claude lúc đó còn quota):
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra [Troubleshooting](#-troubleshooting) section
2. Xem GitHub Issues
3. Tạo Issue mới với chi tiết lỗi

---

**Happy Anime Tracking! 🎬✨**