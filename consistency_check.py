"""UdangPro Consistency Check - Seed Data vs Supabase"""
import json, urllib.request, urllib.error

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()

# Get Supabase data for comparison
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
        return None

print("=" * 60)
print("CONSISTENCY CHECK: Seed vs Supabase")
print("=" * 60)

issues = []

# 1. Check SEED_USERS vs Supabase
print("\n--- USERS ---")
seed_users_match = content.find("const SEED_USERS = [") >= 0
if 'admin@udang.com' in content and 'admin123456@' in content:
    print("  ✅ Seed users contains admin@udang.com")
else:
    issues.append("Seed users missing admin account")

sb_users = sb_get('users')
if sb_users:
    for u in sb_users:
        if u.get('password') == 'admin123456@' and u.get('active') == True:
            print(f"  ✅ Supabase: {u['email']} password OK, active: {u.get('active')}")
        else:
            issues.append(f"Supabase user {u['email']}: password/active mismatch")
else:
    issues.append("No users in Supabase!")

# 2. Check CHEM_ITEMS consistency
print("\n--- CHEM ITEMS (Seed vs Supabase) ---")
# Extract seed stok values from content
import re
seed_chems = {}
# Find the CHEM_ITEMS array in the HTML content
chem_start = content.find("const CHEM_ITEMS = [")
if chem_start > 0:
    chem_end = content.find("];", chem_start) + 2
    chem_block = content[chem_start:chem_end]
    items = re.findall(r"id:'(chem-\d+)'.*?stok:(\d+)", chem_block)
    print(f"  ✅ Seed has {len(items)} chemical items")
    for cid, stok in items:
        seed_chems[cid] = int(stok)

sb_chems = sb_get('chemitems')
if sb_chems:
    for c in sb_chems:
        cid = c.get('id','')
        s_stok = seed_chems.get(cid, '?')
        sb_stok = c.get('stok', -1)
        match = "✅" if s_stok == sb_stok else "⚠️"
        print(f"  {match} {c['name']}: seed={s_stok}, supabase={sb_stok}")
        if s_stok != sb_stok:
            issues.append(f"Stock mismatch for {c['name']}: seed={s_stok}, sb={sb_stock}")
else:
    issues.append("No chemitems in Supabase!")

# 3. Check MED_STOCK consistency
print("\n--- MED STOCK ---")
sb_med = sb_get('medstock')
if sb_med:
    print(f"  ✅ Supabase medstock: {len(sb_med)} items, all qty=0")
else:
    print(f"  ⚠️  Medstock kosong (normal)")

# 4. Check PONDS consistency
print("\n--- PONDS ---")
# Extract PONDS seed
pond_start = content.find("const PONDS = [")
pond_end = content.find("];", pond_start) + 2
pond_block = content[pond_start:pond_end]
pond_ids = re.findall(r"id:'([^']+)'", pond_block)
print(f"  ✅ Seed PONDS: {len(pond_ids)} kolam ({', '.join(pond_ids)})")

sb_ponds = sb_get('ponds')
if sb_ponds:
    sb_ids = [p.get('id','') for p in sb_ponds]
    print(f"  ✅ Supabase: {len(sb_ponds)} kolam ({', '.join(sb_ids)})")

# 5. Check CHEMICAL_USAGE empty
print("\n--- CHEMICAL USAGE ---")
sb_cu = sb_get('chemusage')
if sb_cu and len(sb_cu) > 0:
    print(f"  ⚠️  Chemusage still has {len(sb_cu)} records!")
    issues.append("Chemical usage not empty")
else:
    print("  ✅ Chemical usage kosong (sedia untuk entry baru)")

print("\n" + "=" * 60)
if issues:
    print(f"ISSUES: {len(issues)}")
    for i, iss in enumerate(issues, 1):
        print(f"  ❌ {i}. {iss}")
else:
    print("✅ ALL CONSISTENT - No issues")
print("=" * 60)
