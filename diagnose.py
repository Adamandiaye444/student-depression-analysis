#!/usr/bin/env python3
import sys, time, subprocess

print("="*70)
print("DIAGNOSTIC")
print("="*70)

# Test MongoDB
print("\n[1/3] Test MongoDB...")
start = time.time()
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb+srv://adamandiaye1_db_user:tCLjHu1rz8xtwtds@cluster0.ugjeorv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print(f"    ✓ MongoDB OK ({time.time()-start:.2f}s)")
    client.close()
except Exception as e:
    print(f"    ✗ ERREUR: {e}")

# Test port
print("\n[2/3] Test port 5001...")
result = subprocess.run(['lsof', '-i', ':5001'], capture_output=True, text=True)
if result.stdout:
    print("    ⚠ Port occupé")
else:
    print("    ✓ Port libre")

# Test import app
print("\n[3/3] Test chargement app.py...")
start = time.time()
try:
    import app
    print(f"    ✓ Chargé en {time.time()-start:.2f}s")
except Exception as e:
    print(f"    ✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()