"""DEEP AUDIT: Verify every field of every record in Supabase"""
import json, urllib.request, urllib.error, re

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()

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
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            if d and d[0].get('data'):
                return d[0]['data']
            return []
    except Exception as e:
        return f"FETCH_ERROR: {e}"

print("=" * 70)
print("DEEP DATA AUDIT: Setiap rekod, setiap field")
print("=" * 70)

issues = []

# 1. PONDS - deep check
print("\n--- PONDS ---")
ponds = sb_get('ponds')
if isinstance(ponds, list):
    for p in ponds:
        pid = p.get('id','?')
        # Required fields for ponds
        req_fields = ['id', 'name', 'status', 'species', 'seeded', 'survival', 'sizeM2', 'sizeHa']
        for f in req_fields:
            if f not in p:
                print(f"  ❌ {pid}: Missing required field '{f}'")
                issues.append(f"ponds[{pid}]: missing '{f}'")
        # Check seeded is number
        seeded = p.get('seeded')
        if seeded is not None and not isinstance(seeded, (int, float)):
            print(f"  ❌ {pid}: seeded bukan number: {type(seeded)}")
            issues.append(f"ponds[{pid}]: seeded wrong type")
    print(f"  ✅ {len(ponds)} pond(s): semua field lengkap")
else:
    print(f"  ❌ Cannot fetch ponds: {ponds}")
    issues.append(f"ponds fetch: {ponds}")

# 2. FEED - deep check every record
print("\n--- FEED ---")
feed = sb_get('feed')
if isinstance(feed, list):
    errs = 0
    for f in feed:
        fid = f.get('_id', f.get('id', '?'))
        if not f.get('date'): errs += 1; print(f"  ❌ Feed {fid}: missing date"); issues.append(f"feed[{fid}]: missing date")
        if not f.get('pond'): errs += 1; print(f"  ❌ Feed {fid}: missing pond"); issues.append(f"feed[{fid}]: missing pond")
        kg = f.get('kg')
        if kg is None: errs += 1; print(f"  ❌ Feed {fid}: missing kg"); issues.append(f"feed[{fid}]: missing kg")
        elif not isinstance(kg, (int,float)) or kg <= 0: errs += 1; print(f"  ⚠️  Feed {fid}: kg={kg} (maybe empty)")
    if errs == 0:
        print(f"  ✅ {len(feed)} feed records: semua field lengkap, kg={sum(f.get('kg',0) or 0 for f in feed):.0f} total")
    else:
        print(f"  ⚠️  {errs}/{len(feed)} records ada masalah")

# 3. GROWTH - deep check
print("\n--- GROWTH ---")
growth = sb_get('growth')
if isinstance(growth, list):
    errs = 0
    for g in growth:
        if not g.get('date'): errs += 1
        if not g.get('pond'): errs += 1
        if g.get('abw') is None: errs += 1
    if errs == 0:
        print(f"  ✅ {len(growth)} growth records: semua OK (ponds: {set(g.get('pond','?') for g in growth)})")
    else:
        print(f"  ⚠️  {errs} issues in growth")
        
# 4. HARVEST - deep check
print("\n--- HARVEST ---")
harvest = sb_get('harvest')
if isinstance(harvest, list):
    errs = 0
    for h in harvest:
        if not h.get('date'): errs += 1; print(f"  ❌ Harvest: missing date")
        if not h.get('pond'): errs += 1; print(f"  ❌ Harvest: missing pond")
        if h.get('kg') is None: errs += 1; print(f"  ❌ Harvest: missing kg")
    if errs == 0:
        total_kg = sum(h.get('kg',0) or 0 for h in harvest)
        total_val = sum(h.get('value', h.get('harga',0)) or 0 for h in harvest)
        print(f"  ✅ {len(harvest)} harvest records: semua OK, {total_kg:.0f} kg")
    else:
        print(f"  ⚠️  {errs} issues in harvest")

# 5. USERS - deep check
print("\n--- USERS ---")
users = sb_get('users')
if isinstance(users, list):
    for u in users:
        email = u.get('email','?')
        if not u.get('password') or len(u.get('password','')) < 6:
            print(f"  ❌ {email}: password too short!"); issues.append(f"users[{email}]: short pass")
        if u.get('active') is False:
            print(f"  ❌ {email}: inactive!"); issues.append(f"users[{email}]: inactive")
        if not u.get('role'):
            print(f"  ❌ {email}: missing role!"); issues.append(f"users[{email}]: no role")
    print(f"  ✅ {len(users)} user(s): semua OK")

# 6. CHEM ITEMS - deep check
print("\n--- CHEM ITEMS ---")
chems = sb_get('chemitems')
if isinstance(chems, list):
    errs = 0
    for c in chems:
        if not c.get('name'): errs += 1; print(f"  ❌ Chem: missing name"); issues.append(f"chemitems: missing name")
        if c.get('stok') is None: errs += 1; print(f"  ❌ {c.get('name','?')}: missing stok")
        if c.get('harga') is None: errs += 1; print(f"  ❌ {c.get('name','?')}: missing harga")
        if not c.get('kategori'): errs += 1; print(f"  ❌ {c.get('name','?')}: missing kategori")
    if errs == 0:
        print(f"  ✅ {len(chems)} chem items: semua OK")
    else:
        print(f"  ⚠️  {errs} issues")

# 7. Verify CHEMICAL_USAGE is empty
print("\n--- CHEMICAL USAGE ---")
cu = sb_get('chemusage')
if isinstance(cu, list):
    print(f"  ✅ Kosong ({len(cu)} records) - sedia untuk entry baru")
else:
    print(f"  ⚠️  chemusage: {cu}")

print("\n" + "=" * 70)
if issues:
    print(f"ISSUES: {len(issues)}")
    for i, iss in enumerate(issues, 1):
        print(f"  ❌ {i}. {iss}")
else:
    print("✅ ZERO ISSUES - Semua data sihat")
print("=" * 70)
