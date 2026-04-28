import httpx

base = "http://localhost:8000"

# Test 1: Root heartbeat
r = httpx.get(f"{base}/")
data = r.json()
print(f"Test 1 - Root heartbeat: {r.status_code} | {data.get('message')}")

# Test 2: Industry context
r = httpx.get(f"{base}/api/context")
print(f"Test 2 - Context endpoint: {r.status_code}")
if r.status_code == 200:
    ctx = r.json()
    print(f"         domain_name = {ctx.get('domain_name')}")
    print(f"         expert_role = {ctx.get('expert_role')}")
else:
    print(f"         Response: {r.text}")

# Test 3: Ingest endpoint is reachable (422 = endpoint exists, just needs a file)
r = httpx.post(f"{base}/api/ingest")
print(f"Test 3 - Ingest endpoint live: {r.status_code} (422 = good, means file is required)")
