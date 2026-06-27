import urllib.request, json, time
try:
    data = json.loads(urllib.request.urlopen("http://192.168.1.107:8080/api/reminders", timeout=5).read())
    print(f"OK: {len(data)} reminders, board reachable")
    triggered = [r for r in data if r.get("status") == "triggered"]
    print(f"Triggered: {len(triggered)}")
    if triggered:
        latest = triggered[-1]
        print(f"Latest: {latest.get('title','?')} - {latest.get('content','?')}")
except Exception as e:
    print(f"FAIL: {e}")
