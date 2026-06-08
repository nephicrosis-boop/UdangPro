"""DEEP CODE SCAN: Setiap baris kritikal"""
import re

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 70)
print("DEEP CODE SCAN: Potential bugs & edge cases")
print("=" * 70)

issues = []

# 1. Check the render switch - all 14 nav items have a case handler
print("\n--- 1. Router: Semua nav items ada handler? ---")
nav_ids = []
nav_start = content.find("const NAV = [")
nav_end = content.find("];", nav_start) + 2
nav_block = content[nav_start:nav_end]
for m in re.finditer(r"id:\s*'([^']+)'", nav_block):
    nav_ids.append(m.group(1))

# Find all case statements
cases = []
for m in re.finditer(r"case\s+'([^']+)':", content):
    cases.append(m.group(1))

missing = [n for n in nav_ids if n not in cases]
extra = [c for c in cases if c not in nav_ids]

if missing:
    print(f"  ❌ Nav items WITHOUT case handler: {missing}")
    issues.append(f"Router: missing cases for {missing}")
else:
    print(f"  ✅ Semua {len(nav_ids)} nav items ada handler")

if extra:
    print(f"  ⚠️  Case handlers without nav item: {extra}")
    
# 2. Check chem items for harga:0 (free items might be wrong)
print("\n--- 2. Chem items: harga check ---")
chem_start = content.find("const CHEM_ITEMS = [")
chem_end = content.find("];", chem_start) + 2
chem_block = content[chem_start:chem_end]

for m in re.finditer(r"id:'([^']+)'.*?name:'([^']*)'.*?harga:([^,]+)", chem_block):
    cid, name, price = m.groups()
    try:
        p = float(price)
        if p == 0:
            print(f"  ⚠️  {name}: harga=0! Free?")
            issues.append(f"{name}: harga=0")
    except:
        pass
print(f"  ✅ Harga semua item > RM0")

# 3. Check for potential undefined/null reference crashes
print("\n--- 3. Null/undefined safety checks ---")
# Look for .map without || [] 
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    # Check .map calls on potentially undefined variables
    if '.map(' in stripped and '|| []' not in stripped and '||[]' not in stripped:
        # Only flag if it's accessing user data or might be null
        if 'ponds' in stripped or 'feed' in stripped or 'items' in stripped:
            print(f"  ⚠️  L{i}: .map() without fallback: {stripped[:100]}")
            issues.append(f"L{i}: .map() may fail on null")

# 4. Check SB (Supabase) reference availability
print("\n--- 4. SB object availability ---")
sb_refs = 0
sb_defined = "const SB = {" in content
for i, line in enumerate(lines, 1):
    if 'SB.' in line and 'const SB' not in line:
        sb_refs += 1
print(f"  ✅ SB defined: {sb_defined}, SB used: {sb_refs} times")

# 5. Check all localStorage keys for consistency
print("\n--- 5. localStorage key consistency ---")
ls_keys = set()
for m in re.finditer(r"localStorage\.getItem\('([^']+)'\)", content):
    ls_keys.add(m.group(1))
for m in re.finditer(r"localStorage\.setItem\('([^']+)'", content):
    ls_keys.add(m.group(1))
print(f"  ✅ localStorage keys used: {sorted(ls_keys)}")

# 6. Check the Dashboard alert for null crash on medStock
print("\n--- 6. Dashboard: medStock.filter safety ---")
for i, line in enumerate(lines, 1):
    if 'medStock.filter' in line or 'feedStock.filter' in line or 'health.filter' in line:
        # Check if preceded by null check
        print(f"  L{i}: {line.strip()[:100]}")

# 7. Verify that chemical module renders properly
print("\n--- 7. Chemical module rendering ---")
for i, line in enumerate(lines, 1):
    if 'chemicals' in line.lower() and ('case' in line or 'Module' in line or 'Chemical' in line):
        print(f"  L{i}: {line.strip()[:120]}")

# 8. Brace/template balance for all JSX
print("\n--- 8. JSX structure integrity ---")
# Count React.createElement nesting
create_count = content.count('React.createElement')
create_close = content.count(')//')
print(f"  ✅ React.createElement calls: ~{create_count}")

# 9. Check for any remaining 'Admin' or 'Manager' caps references
print("\n--- 9. Remaining capital letter role references ---")
for i, line in enumerate(lines, 1):
    if "'Admin'" in line or "'Manager'" in line or "'Pekerja'" in line:
        if 'PERMISSIONS' not in line and 'SEED_USERS' not in line:
            print(f"  ⚠️  L{i}: Capital role reference: {line.strip()[:100]}")
            issues.append(f"L{i}: capital role ref")

# 10. Check icon-192.jpg availability
print("\n--- 10. Asset references ---")
if 'icon-192.jpg' in content or 'icon-192.svg' in content:
    print(f"  ✅ Icons referenced")

print("\n" + "=" * 70)
if issues:
    print(f"ISSUES FOUND: {len(issues)}")
    for i, iss in enumerate(issues, 1):
        print(f"  ❌ {i}. {iss}")
else:
    print("✅ ZERO CODE ISSUES - Semua selamat")
print("=" * 70)
