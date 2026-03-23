import requests
from datetime import datetime

# 1. The URL of your local Django server
url = "http://127.0.0.1:8000/iclock/cdata"

# 2. Get the current exact time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 3. The raw string exactly how ZKTeco sends it (Replace EMP001 with an ID that exists in your database!)
# Format: ID \t Time \t Status(0=In) \t Verify(15=Face) \t WorkCode \t Reserved
raw_zkteco_data = f"EMP001\t{current_time}\t0\t15\t0\t0"

print(f"📡 Sending fake punch to server: {raw_zkteco_data}")

# 4. Shoot the data to Django
response = requests.post(url, data=raw_zkteco_data.encode('utf-8'))

print(f"🎯 Server Response: {response.status_code} - {response.text}")