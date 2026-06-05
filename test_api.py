import requests
import json

player_id = 91845  # Son Heung-min
url = f"https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history"

print(f"Testing API for Son Heung-min (ID: {player_id})")
print(f"URL: {url}")
print()

response = requests.get(url, timeout=10)
print(f"Status Code: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    print("Response keys:", list(data.keys()))
    print()
    
    if 'marketValueHistory' in data:
        history = data['marketValueHistory']
        print(f"Total history entries: {len(history)}")
        print()
        print("Last 5 entries:")
        for entry in history[-5:]:
            print(json.dumps(entry, indent=2))
    else:
        print("No 'marketValueHistory' key found")
        print("Full response:")
        print(json.dumps(data, indent=2)[:500])
else:
    print(f"Error: {response.text[:200]}")

# Made with Bob
