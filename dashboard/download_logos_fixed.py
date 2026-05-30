#!/usr/bin/env python3
"""Download World Cup logos properly."""
import requests
import os

# Create logos directory
os.makedirs('logos', exist_ok=True)

# Direct image URLs from Wikimedia Commons
logos = {
    1998: 'https://upload.wikimedia.org/wikipedia/en/1/11/1998_FIFA_World_Cup_logo.svg',
    2002: 'https://upload.wikimedia.org/wikipedia/en/3/33/2002_FIFA_World_Cup_logo.svg',
    2006: 'https://upload.wikimedia.org/wikipedia/en/6/66/2006_FIFA_World_Cup_logo.svg',
    2010: 'https://upload.wikimedia.org/wikipedia/en/a/a8/2010_FIFA_World_Cup_logo.svg',
    2014: 'https://upload.wikimedia.org/wikipedia/en/9/90/2014_FIFA_World_Cup_logo.svg',
    2018: 'https://upload.wikimedia.org/wikipedia/en/6/67/2018_FIFA_World_Cup_logo.svg',
    2022: 'https://upload.wikimedia.org/wikipedia/en/e/e3/2022_FIFA_World_Cup.svg',
    2026: 'https://upload.wikimedia.org/wikipedia/en/f/f8/2026_FIFA_World_Cup_logo.svg'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

for year, url in logos.items():
    print(f'Downloading {year}...')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(f'logos/wc_{year}.svg', 'wb') as f:
                f.write(response.content)
            print(f'  ✓ {len(response.content)} bytes')
        else:
            print(f'  ✗ Failed: {response.status_code}, {len(response.content)} bytes')
    except Exception as e:
        print(f'  ✗ Error: {e}')

print('\nDone!')

# Made with Bob
