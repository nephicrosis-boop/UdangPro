"""UdangPro Full Audit - Check All Data & Code"""
import json, urllib.request, urllib.error

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()

# Extract Supabase creds
def extract_var(name):
    s = content.find(f"{name} = '") + len(f"{name} = '")
    return content[s:content.find("'", s)]

key = extract_var("SUPABASE_ANON")
url_base = extract_var("SUPABASE_URL")

def sb_get(id_name):
    req = urllib.request.Request(f'{url_base}/rest/v1/farm_data?id=eq.{id_name}')
    req.add_header('apikey', key)
    req.add_header('Authorization', f'Bearer {key}')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            if d and d[0].get('data'):
                return d[0]['data']
            return []
    except Exception as e:
        return f"ERROR: {e}"

print("=" * 60)
print("U D A N G P R O   F U L L   A U D I T")
print("=" * 60)

# 1. Check all Supabase data keys
print("\n--- DATA INTEGRITY CHECK ---")
issues = []

keys_to_check = {
    'ponds': 'Kolam records',
    'feed': 'Feed records',
    'growth': 'Growth records',
    'harvest': 'Harvest records',
    'feedstock': 'Feed stock',
    'chemitems': 'Chemical items',
    'chemusage': 'Chemical usage',
    'medstock': 'Medicine stock',
    'users': 'User accounts',
    'stockitems': 'Stock items',
    'stockmoves': 'Stock movements',
    'suppliers': 'Suppliers',
}

for kid, desc in keys_to_check.items():
    data = sb_get(kid)
    if isinstance(data, str):
        print(f"  ⚠️  {kid} ({desc}): {data}")
        issues.append(f"{kid}: fetch error")
    elif len(data) == 0:
        print(f"  ⚠️  {kid} ({desc}): EMPTY (kosong)")
    else:
        print(f"  ✅ {kid} ({desc}): {len(data)} records")

# 2. Check PONDS data structure
print("\n--- PONDS CHECK ---")
ponds = sb_get('ponds')
if isinstance(ponds, list) and ponds:
    for p in ponds:
        required = ['id', 'name', 'status', 'species', 'seeded', 'survival']
        missing = [r for r in required if r not in p]
        if missing:
            print(f"  ⚠️  Pond {p.get('id','?')}: missing fields {missing}")
            issues.append(f"pond {p.get('id','?')}: missing {missing}")
        else:
            print(f"  ✅ Pond {p['id']}: {p.get('name','?')} - {p['status']} - {p.get('species','?')}")
else:
    issues.append("No ponds data!")

# 3. Check FEED data
print("\n--- FEED CHECK ---")
feed = sb_get('feed')
if isinstance(feed, list):
    if len(feed) > 0:
        total_kg = sum(f.get('kg', 0) or 0 for f in feed)
        ponds_in_feed = set(f.get('pond','') for f in feed)
        print(f"  ✅ Feed records: {len(feed)}, total {total_kg:.0f} kg")
        print(f"  ✅ Ponds with feed: {ponds_in_feed}")
    else:
        print(f"  ⚠️  Feed: kosong")
else:
    issues.append("Feed data issue")

# 4. Check GROWTH
print("\n--- GROWTH CHECK ---")
growth = sb_get('growth')
if isinstance(growth, list):
    if len(growth) > 0:
        print(f"  ✅ Growth records: {len(growth)}")
        ponds_in_growth = set(g.get('pond','') for g in growth)
        print(f"  ✅ Ponds with growth: {ponds_in_growth}")
    else:
        print(f"  ⚠️  Growth: kosong")

# 5. Check USERS
print("\n--- USERS CHECK ---")
users = sb_get('users')
if isinstance(users, list) and users:
    for u in users:
        pw = u.get('password', '')
        if not pw or len(pw) < 6:
            print(f"  ⚠️  User {u.get('email','?')}: short password!")
            issues.append(f"User {u['email']}: password too short")
        if not u.get('active', True):
            print(f"  ⚠️  User {u.get('email','?')}: inactive!")
            issues.append(f"User {u['email']}: inactive")
        print(f"  ✅ User: {u.get('email','?')} role={u.get('role','?')}")

# 6. Check CHEM ITEMS
print("\n--- CHEM ITEMS CHECK ---")
chems = sb_get('chemitems')
if isinstance(chems, list) and chems:
    for c in chems:
        if c.get('stok', 0) < 0:
            print(f"  ⚠️  {c.get('name','?')}: negative stock {c['stok']}")
            issues.append(f"{c['name']}: negative stock")
        else:
            print(f"  ✅ {c.get('name','?')}: stok={c.get('stok',0)} {c.get('unit','?')} @ RM{c.get('harga',0)}")

# 7. Check HARVEST
print("\n--- HARVEST CHECK ---")
harvest = sb_get('harvest')
if isinstance(harvest, list) and harvest:
    total_h = sum(h.get('kg', 0) or 0 for h in harvest)
    print(f"  ✅ Harvest records: {len(harvest)}, total {total_h:.0f} kg")
else:
    print(f"  ⚠️  Harvest: kosong")

print("\n" + "=" * 60)
print(f"AUDIT COMPLETE")
print(f"Issues found: {len(issues)}")
for i, iss in enumerate(issues, 1):
    print(f"  {i}. {iss}")
print("=" * 60)
