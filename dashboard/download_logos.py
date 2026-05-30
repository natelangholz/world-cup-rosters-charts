#!/usr/bin/env python3
"""Download World Cup logos for the dashboard."""
import requests
import os

# World Cup logo URLs
logos = {
    1998: 'https://upload.wikimedia.org/wikipedia/en/1/11/1998_FIFA_World_Cup_logo.svg',
    2002: 'https://upload.wikimedia.org/wikipedia/en/3/33/2002_FIFA_World_Cup_logo.svg',
    2006: 'https://upload.wikimedia.org/wikipedia/en/6/66/2006_FIFA_World_Cup_logo.svg',
    2010: 'https://upload.wikimedia.org/wikipedia/en/a/a8/2010_FIFA_World_Cup_logo.svg',
    2014: 'https://upload.wikimedia.org/wikipedia/en/9/90/2014_FIFA_World_Cup_logo.svg',
    2018: 'https://upload.wikimedia.org/wikipedia/en/6/67/2018_FIFA_World_Cup_logo.svg',
    2022: 'https://upload.wikimedia.org/wikipedia/en/e/e3/2022_FIFA_World_Cup.svg'
}

# Create logos directory
os.makedirs('logos', exist_ok=True)

for year, url in logos.items():
    print(f'Downloading {year} logo...')
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'logos/wc_{year}.svg', 'wb') as f:
            f.write(response.content)
        print(f'  ✓ Saved logos/wc_{year}.svg')
    else:
        print(f'  ✗ Failed to download {year}')

print('\nDone!')

# Made with Bob
