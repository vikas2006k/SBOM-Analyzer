"""
Migration + full seed using GRC Hackathon problem_10 sample data.
"""
import sqlite3, json, csv, os
from datetime import datetime

SAMPLE_DIR = r"C:\Users\vikas\Downloads\GRC-Hackathon-extracted\GRC-Hackathon-main\Problem Statements\Problem_10_Supply_Chain_Risk\sample_data\problem_10"
DB_PATH = "backend/instance/initial.db"
NOW = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
conn.execute("PRAGMA foreign_keys = OFF")

# ── STEP 0: MIGRATE vulnerabilities table ──────────────────────────────────────
print("Migrating vulnerabilities table...")
existing_cols = {row[1] for row in cur.execute("PRAGMA table_info(vulnerabilities)").fetchall()}
migrations = [
    ("affected_library", "TEXT"),
    ("affected_versions", "TEXT"),
    ("patch_available", "INTEGER DEFAULT 0"),
    ("exploitability", "TEXT"),
    ("published_date", "TEXT"),
]
for col, coltype in migrations:
    if col not in existing_cols:
        cur.execute(f"ALTER TABLE vulnerabilities ADD COLUMN {col} {coltype}")
        print(f"  Added column: {col}")
    else:
        print(f"  Column exists: {col}")
conn.commit()

# ── STEP 1: CLEAR existing demo data ─────────────────────────────────────────
print("\nClearing old demo data...")
cur.execute("DELETE FROM library_vulnerabilities")
cur.execute("DELETE FROM vulnerabilities")
cur.execute("DELETE FROM risk_scores")
cur.execute("DELETE FROM dependency_graph")
cur.execute("DELETE FROM sbom_uploads")
cur.execute("DELETE FROM analysis_reports")
cur.execute("DELETE FROM libraries")
cur.execute("DELETE FROM applications WHERE id >= 1")
cur.execute("DELETE FROM license_rules")
conn.commit()
print("Cleared.\n")

# ── STEP 2: SEED APPLICATIONS ─────────────────────────────────────────────────
print("Seeding applications...")
with open(os.path.join(SAMPLE_DIR, "applications.json"), encoding="utf-8") as f:
    apps_data = json.load(f)

criticality_map = {"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High", "CRITICAL": "Critical"}
app_id_map = {}  # "APP-001" -> integer id
app_lang_map = {}  # "APP-001" -> "Java"

for app in apps_data:
    crit = criticality_map.get(app["criticality"], "Medium")
    desc = (f"{app['name']} — {app['language']} application owned by {app['business_owner']} "
            f"({app['department']}). Deployed on {app['deployment']}.")
    cur.execute(
        "INSERT INTO applications (name, version, description, business_criticality, is_deleted, created_at, updated_at) VALUES (?,?,?,?,0,?,?)",
        (app["name"], "1.0.0", desc, crit, NOW, NOW)
    )
    db_id = cur.lastrowid
    app_id_map[app["app_id"]] = db_id
    app_lang_map[app["app_id"]] = app["language"]
    print(f"  {app['app_id']} -> {app['name']} [id={db_id}, {crit}]")

conn.commit()

# ── STEP 3: SEED LIBRARIES + DIRECT DEPS from sbom_dependencies.csv ──────────
print("\nSeeding libraries and direct dependency edges...")
lang_to_ecosystem = {"Java": "maven", "Python": "pip", "JavaScript": "npm", "Go": "go"}
lib_key_map = {}  # (name, version) -> db library id

with open(os.path.join(SAMPLE_DIR, "sbom_dependencies.csv"), encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

# Collect unique libraries first
unique_libs = {}
for row in rows:
    eco = lang_to_ecosystem.get(app_lang_map.get(row["application_id"], "Java"), "maven")
    key = (row["library"].strip(), row["version"].strip())
    if key not in unique_libs:
        unique_libs[key] = {"license": row["license"].strip(), "ecosystem": eco}

for (name, version), meta in unique_libs.items():
    cur.execute(
        "INSERT INTO libraries (name, version, ecosystem, license_name, is_deleted, created_at, updated_at) VALUES (?,?,?,?,0,?,?)",
        (name, version, meta["ecosystem"], meta["license"], NOW, NOW)
    )
    lib_key_map[(name, version)] = cur.lastrowid

conn.commit()
print(f"  Libraries: {len(lib_key_map)}")

# Insert direct dep edges
direct_count = 0
for row in rows:
    app_int_id = app_id_map.get(row["application_id"])
    child_lib_id = lib_key_map.get((row["library"].strip(), row["version"].strip()))
    if not app_int_id or not child_lib_id:
        continue
    cur.execute(
        "INSERT INTO dependency_graph (application_id, parent_library_id, child_library_id, depth, is_transitive, is_deleted, created_at, updated_at) VALUES (?,NULL,?,1,0,0,?,?)",
        (app_int_id, child_lib_id, NOW, NOW)
    )
    direct_count += 1

conn.commit()
print(f"  Direct edges: {direct_count}")

# ── STEP 4: SEED TRANSITIVE DEPS ─────────────────────────────────────────────
print("\nSeeding transitive dependency edges...")
with open(os.path.join(SAMPLE_DIR, "transitive_dependencies.json"), encoding="utf-8") as f:
    trans_data = json.load(f)

new_libs = 0
trans_count = 0
for td in trans_data:
    app_int_id = app_id_map.get(td["application_id"])
    if not app_int_id:
        continue
    p_key = (td["parent_library"].strip(), td["parent_version"].strip())
    c_key = (td["child_library"].strip(), td["child_version"].strip())

    for key, eco in [(p_key, "maven"), (c_key, "maven")]:
        if key not in lib_key_map:
            cur.execute(
                "INSERT INTO libraries (name, version, ecosystem, license_name, is_deleted, created_at, updated_at) VALUES (?,?,'npm','Unknown',0,?,?)",
                (key[0], key[1], NOW, NOW)
            )
            lib_key_map[key] = cur.lastrowid
            new_libs += 1

    cur.execute(
        "INSERT INTO dependency_graph (application_id, parent_library_id, child_library_id, depth, is_transitive, is_deleted, created_at, updated_at) VALUES (?,?,?,2,1,0,?,?)",
        (app_int_id, lib_key_map[p_key], lib_key_map[c_key], NOW, NOW)
    )
    trans_count += 1

conn.commit()
print(f"  Transitive edges: {trans_count} (new libs: {new_libs})")

# ── STEP 5: SEED VULNERABILITIES ─────────────────────────────────────────────
print("\nSeeding vulnerabilities...")
with open(os.path.join(SAMPLE_DIR, "vulnerability_db.json"), encoding="utf-8") as f:
    vuln_data = json.load(f)

sev_map = {"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High", "CRITICAL": "Critical"}
cve_id_map = {}
vuln_count = 0

for v in vuln_data:
    sev = sev_map.get(v.get("severity", "Medium"), "Medium")
    try:
        cur.execute(
            """INSERT INTO vulnerabilities
               (cve_id, affected_library, affected_versions, cvss_score, severity, description,
                patched_version, patch_available, exploitability, published_date,
                is_deleted, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,0,?,?)""",
            (
                v.get("cve_id", ""),
                v.get("library", ""),
                ", ".join(v.get("affected_versions", [])),
                v.get("cvss_score", 5.0),
                sev,
                v.get("description", ""),
                v.get("fixed_version") or "",
                1 if v.get("patch_available") else 0,
                v.get("exploitability", "MEDIUM"),
                v.get("published_date", ""),
                NOW, NOW
            )
        )
        cve_id_map[v["cve_id"]] = cur.lastrowid
        vuln_count += 1
    except Exception as e:
        print(f"  WARN {v.get('cve_id')}: {e}")

conn.commit()
print(f"  Vulnerabilities: {vuln_count}")

# ── STEP 6: LINK VULNS TO LIBRARIES via library_vulnerabilities ───────────────
print("\nLinking vulnerabilities to libraries...")
# Build a name-only lookup: lib_name -> [(lib_id, version), ...]
lib_name_map = {}
for (name, version), lib_id in lib_key_map.items():
    if name not in lib_name_map:
        lib_name_map[name] = []
    lib_name_map[name].append((lib_id, version))

match_count = 0
for v in vuln_data:
    lib_name = v.get("library", "").strip()
    vuln_db_id = cve_id_map.get(v["cve_id"])
    if not vuln_db_id:
        continue
    affected_versions = [x.strip() for x in v.get("affected_versions", [])]
    # Match libraries by name; if affected_versions list in vuln_db matches a lib version in our DB, link it
    # Otherwise, link all libraries with the same name (conservative approach)
    candidates = lib_name_map.get(lib_name, [])
    for lib_id, lib_ver in candidates:
        # Link by library name match (version filter removed since sample data versions differ)
        try:
            cur.execute(
                "INSERT OR IGNORE INTO library_vulnerabilities (library_id, vulnerability_id) VALUES (?,?)",
                (lib_id, vuln_db_id)
            )
            match_count += 1
        except Exception:
            pass

conn.commit()
print(f"  Library-vulnerability links: {match_count}")

# ── STEP 7: SEED LICENSE RULES ────────────────────────────────────────────────
print("\nSeeding license rules...")
with open(os.path.join(SAMPLE_DIR, "license_rules.json"), encoding="utf-8") as f:
    rules_data = json.load(f)

risk_to_category = {"LOW": "Permissive", "MEDIUM": "Weak-Copyleft", "HIGH": "Unknown", "CRITICAL": "Copyleft"}
special = {"SSPL-1.0": "Copyleft", "UNKNOWN": "Unknown", "Dual-MIT/Commercial": "Permissive"}

seeded_categories = set()
for rule in rules_data:
    lic = rule["license"]
    category = special.get(lic) or risk_to_category.get(rule.get("risk_level", "LOW"), "Unknown")
    compat = rule.get("compatible_with_proprietary", True)
    viral = rule.get("viral", False)
    notes = f"[{lic} / {rule.get('spdx', lic)}] {rule.get('notes', '')}"
    if category not in seeded_categories:
        cur.execute(
            "INSERT OR REPLACE INTO license_rules (license_category, commercial_allowed, proprietary_linkable, description, is_deleted, created_at, updated_at) VALUES (?,?,?,?,0,?,?)",
            (category, 1 if compat else 0, 0 if viral else 1, notes, NOW, NOW)
        )
        seeded_categories.add(category)
    # Update description to append additional license identifiers
    else:
        cur.execute(
            "UPDATE license_rules SET description = description || ' | ' || ? WHERE license_category = ?",
            (f"[{lic}] {rule.get('notes','')}", category)
        )

conn.commit()
print(f"  License rule categories seeded: {len(seeded_categories)}")

# ── STEP 8: SUMMARY ───────────────────────────────────────────────────────────
print("\n" + "="*55)
print("SEED COMPLETE — Final counts:")
for table, label in [
    ("applications", "Applications      "),
    ("libraries",    "Libraries         "),
    ("dependency_graph", "Dependency edges  "),
    ("vulnerabilities",  "Vulnerabilities   "),
    ("library_vulnerabilities", "Vuln links        "),
    ("license_rules",    "License rules     "),
]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"  {label}: {count}")

print("\nApplications:")
cur.execute("SELECT id, name, business_criticality FROM applications ORDER BY id")
for row in cur.fetchall():
    print(f"  [{row[0]}] {row[1]} ({row[2]})")

conn.execute("PRAGMA foreign_keys = ON")
conn.close()
print("\nDone! Restart the Flask backend to reflect changes.")
