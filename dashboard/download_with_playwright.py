#!/usr/bin/env python3
"""Download World Cup logos using Playwright."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
import time

logos = {
    1998: 'https://upload.wikimedia.org/wikipedia/en/1/11/1998_FIFA_World_Cup_logo.svg',
    2002: 'https://upload.wikimedia.org/wikipedia/en/3/33/2002_FIFA_World_Cup_logo.svg',
    2006: 'https://upload.wikimedia.org/wikipedia/en/6/66/2006_FIFA_World_Cup_logo.svg',
    2010: 'https://upload.wikimedia.org/wikipedia/en/a/a8/2010_FIFA_World_Cup_logo.svg',
    2014: 'https://upload.wikimedia.org/wikipedia/en/9/90/2014_FIFA_World_Cup_logo.svg',
    2018: 'https://upload.wikimedia.org/wikipedia/en/6/67/2018_FIFA_World_Cup_logo.svg',
    2026: 'https://upload.wikimedia.org/wikipedia/en/f/f8/2026_FIFA_World_Cup_logo.svg'
}

os.makedirs('logos', exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    for year, url in logos.items():
        print(f'Downloading {year}...')
        try:
            response = page.goto(url, wait_until='networkidle', timeout=30000)
            if response and response.status == 200:
                content = response.body()
                if len(content) > 1000:
                    with open(f'logos/wc_{year}.svg', 'wb') as f:
                        f.write(content)
                    print(f'  ✓ {len(content)} bytes')
                else:
                    print(f'  ✗ Too small: {len(content)} bytes')
            else:
                print(f'  ✗ Status: {response.status if response else "None"}')
            time.sleep(1)
        except Exception as e:
            print(f'  ✗ Error: {e}')
    
    browser.close()

print('\nDone! Checking files...')
os.system('ls -lh logos/ && file logos/wc_1998.svg')

# Made with Bob
