import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Test: thử select từ bảng novels (đang rỗng cũng được)
response = supabase.table("novels").select("*").limit(5).execute()
print("Kết nối thành công!")
print(response.data)