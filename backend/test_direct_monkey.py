import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"

endpoints = [
    ("/financials/ai-vendor-roi", "AI CFO Vendor ROI"),
    ("/staff/ai-burnout-radar", "AI Burnout Radar"),
    ("/reservations/ai-guest-journey", "AI Guest Journey"),
    ("/revenue/ai-market-intel", "AI Market Intel")
]

print("Starting Monkey Tests (Direct Server Hit)...")

succ = 0
for path, name in endpoints:
    url = f"{BASE_URL}{path}"
    print(f"\n[GET] {url} - {name}...")
    try:
        t0 = time.time()
        res = requests.get(url, timeout=30)
        t1 = time.time()
        print(f"Status: {res.status_code} in {t1-t0:.2f}s")
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                succ += 1
                print("SUCCESS payload received:")
                # Print a summary
                for k, v in data.items():
                    if isinstance(v, (dict, list)):
                        preview = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
                        print(f"  {k}: {preview}")
                    else:
                        print(f"  {k}: {v}")
            else:
                print(f"Failed Payload: {data}")
        else:
            print(f"Error Body: {res.text}")
    except Exception as e:
        print(f"Exception: {e}")

print(f"\nCompleted: {succ}/{len(endpoints)} successful.")
if succ == len(endpoints):
    sys.exit(0)
sys.exit(1)
