import json, urllib.request

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()

key_start = content.find("SUPABASE_ANON = '") + len("SUPABASE_ANON = '")
key_end = content.find("'", key_start)
key = content[key_start:key_end]

url_start = content.find("SUPABASE_URL = '") + len("SUPABASE_URL = '")
url_end = content.find("'", url_start)
url_base = content[url_start:url_end]

users_data = [
    {"id":"u1","email":"admin@udang.com","password":"admin123456@","nama":"Admin","role":"admin","notel":"","createdAt":"2026-01-01","active":True}
]

payload = json.dumps({"id": "users", "data": users_data}).encode()

req = urllib.request.Request(
    f'{url_base}/rest/v1/farm_data',
    data=payload,
    method='POST'
)
req.add_header('apikey', key)
req.add_header('Authorization', f'Bearer {key}')
req.add_header('Content-Type', 'application/json')
req.add_header('Prefer', 'resolution=merge-duplicates')

try:
    with urllib.request.urlopen(req) as r:
        print(f"Status: {r.status}")
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode())

# Verify
req2 = urllib.request.Request(f'{url_base}/rest/v1/farm_data?id=eq.users')
req2.add_header('apikey', key)
req2.add_header('Authorization', f'Bearer {key}')
with urllib.request.urlopen(req2) as r:
    d = json.loads(r.read())
    if d:
        u = d[0]['data'][0]
        print(f"Email: {u['email']} | Password: {u['password']} | Active: {u.get('active')}")
