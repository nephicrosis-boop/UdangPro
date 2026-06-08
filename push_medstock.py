import json, urllib.request

# Read config from index.html
with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html') as f:
    for line in f:
        if 'SUPABASE_ANON' in line:
            key = line.split("'")[1]
            break
        if 'SUPABASE_URL' in line:
            url_base = line.split("'")[1]

# Push medstock reset
data = json.dumps({
    "id": "medstock",
    "data": [
        {"item":"Hydrated Lime (Kapur)", "unit":"kg", "qty":0, "reorder":50},
        {"item":"Sodium Bikarbonat", "unit":"kg", "qty":0, "reorder":5},
        {"item":"Molases", "unit":"kg", "qty":0, "reorder":5},
        {"item":"Kalsium Karbonat", "unit":"kg", "qty":0, "reorder":5},
        {"item":"Super Bio (Probiotik)", "unit":"kg", "qty":0, "reorder":2},
        {"item":"Azomite", "unit":"kg", "qty":0, "reorder":2},
        {"item":"Klorin", "unit":"kg", "qty":0, "reorder":1}
    ]
}).encode()

req = urllib.request.Request(
    f"{url_base}/rest/v1/farm_data",
    data=data,
    method='POST'
)
req.add_header('apikey', key)
req.add_header('Authorization', f'Bearer {key}')
req.add_header('Content-Type', 'application/json')
req.add_header('Prefer', 'resolution=merge-duplicates')

try:
    with urllib.request.urlopen(req) as r:
        print(f"Status: {r.status}")
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error: {e.code} {e.reason}")
    print(e.read().decode())

# Verify
req2 = urllib.request.Request(f"{url_base}/rest/v1/farm_data?id=eq.medstock")
req2.add_header('apikey', key)
req2.add_header('Authorization', f'Bearer {key}')
with urllib.request.urlopen(req2) as r:
    d = json.loads(r.read())
    items = d[0]['data']
    for i in items:
        print(f"  {i['item']}: qty={i['qty']}")
