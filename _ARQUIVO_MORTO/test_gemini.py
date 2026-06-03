import urllib.request, json, sys

key = sys.argv[1] if len(sys.argv) > 1 else "AIzaSyA5kBAjxzvBceHb9cVWR3sR6OE8jG6DJaA"
body = json.dumps({"contents":[{"parts":[{"text":"responda apenas OK"}]}]}).encode()
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
try:
    r = urllib.request.urlopen(req, timeout=15)
    data = json.loads(r.read())
    print("OK!", data["candidates"][0]["content"]["parts"][0]["text"])
except Exception as e:
    print("ERRO:", e)
    if hasattr(e, 'read'):
        print(e.read().decode())
