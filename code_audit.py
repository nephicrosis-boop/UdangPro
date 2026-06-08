"""UdangPro Code Audit - Check for bugs in index.html"""
import re

with open('C:/Users/Draculina/Documents/NephoVault/ShrimpFarmApp/udangpro-cloud/index.html', encoding='utf-8') as f:
    lines = f.readlines()

print("=" * 60)
print("C O D E   A U D I T")
print("=" * 60)

issues = []

# 1. Check all PERMISSIONS references
print("\n--- 1. PERMISSIONS reference check ---")
for i, line in enumerate(lines, 1):
    if 'PERMISSIONS' in line or 'canSee' in line:
        print(f"  L{i}: {line.rstrip()[:120]}")

# 2. Check for {user.name} or {u.name} usages
print("\n--- 2. name vs nama check ---")
for i, line in enumerate(lines, 1):
    if 'u.name' in line and '||' not in line and 'u.nama' not in line:
        print(f"  ⚠️  L{i}: {line.rstrip()[:120]}")
        issues.append(f"L{i}: bare u.name (no || u.nama)")

# 3. Check session storage for name
print("\n--- 3. Session name field ---")
for i, line in enumerate(lines, 1):
    if 'name:' in line and 'sess' in line.lower():
        print(f"  L{i}: {line.rstrip()[:120]}")

# 4. Check all ROLES/PERMISSIONS usage in canSee
print("\n--- 4. canSee function ---")
for i, line in enumerate(lines, 1):
    if 'canSee' in line or 'function canSee' in line:
        print(f"  L{i}: {line.rstrip()[:120]}")

# 5. Check for empty onClick or broken handlers in sidebar
print("\n--- 5. Sidebar nav item navigation ---")
for i, line in enumerate(lines, 1):
    if 'setActive' in line and 'nav' in line.lower():
        print(f"  L{i}: {line.rstrip()[:120]}")

# 6. Check chemusage / chemical routing
print("\n--- 6. Chemical module routing ---")
for i, line in enumerate(lines, 1):
    if 'chemicals' in line.lower() and ('switch' in line.lower() or 'case' in line.lower() or 'active' in line.lower()):
        print(f"  L{i}: {line.rstrip()[:120]}")

# 7. Check overall brace balance
opens = sum(line.count('(') + line.count('[') + line.count('{') for line in lines)
closes = sum(line.count(')') + line.count(']') + line.count('}') for line in lines)
diff = opens - closes
print(f"\n--- 7. Brace balance ---")
print(f"  Open: {opens}, Close: {closes}, Diff: {diff}")
if abs(diff) > 5:
    print(f"  ⚠️  Brace imbalance!")
    issues.append(f"Brace imbalance: {diff}")
else:
    print(f"  ✅ Balanced (diff within tolerance)")

# 8. Check if 'navbar' or 'navTitle' function exists and works
print("\n--- 8. Nav title/routing function ---")
for i, line in enumerate(lines, 1):
    if 'navTitle' in line or 'function navTitle' in line:
        print(f"  L{i}: {line.rstrip()[:120]}")

# 9. Look for the render/switch function that maps active page
print("\n--- 9. Active page rendering ---")
found_render = False
for i, line in enumerate(lines, 1):
    if 'function render' in line or 'const render' in line:
        found_render = True
        # Print the next few lines for context
        for j in range(i, min(i+10, len(lines)+1)):
            print(f"  L{j}: {lines[j-1].rstrip()[:120]}")

if not found_render:
    # Look for the main app switch
    for i, line in enumerate(lines, 1):
        if 'switch' in line and 'active' in line.lower() and 'case' in line.lower():
            print(f"  L{i}: {line.rstrip()[:120]}")

print("\n" + "=" * 60)
if issues:
    print(f"ISSUES FOUND: {len(issues)}")
    for iss in issues:
        print(f"  ❌ {iss}")
else:
    print("✅ NO CODE ISSUES FOUND")
print("=" * 60)
