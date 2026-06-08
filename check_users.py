import json, urllib.request

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()

# Extract key and url
key_start = content.find("SUPABASE_ANON = '") + len("SUPABASE_ANON = '")
key_end = content.find("'", key_start)
key = content[key_start:key_end]

url_start = content.find("SUPABASE_URL = '") + len("SUPABASE_URL = '")
url_end = content.find("'", url_start)
url_base = content[url_start:url_end]

print(f"Key length: {len(key)}")
print(f"URL: {url_base}")

# Check if users exist in Supabase
req = urllib.request.Request(f'{url_base}/rest/v1/farm_data?id=eq.users')
req.add_header('apikey', key)
req.add_header('Authorization', f'Bearer {key}')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read())
    if d and d[0].get('data'):
        users = d[0]['data']
        for u in users:
            print(f"  {u.get('email','?')}: role={u.get('role','?')} password={u.get('password','?')}")
    else:
        print('No users key in Supabase')
        print(f"Response: {d}")
