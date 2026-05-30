"""
Extract market value data from Transfermarkt - trying multiple selector approaches.
"""

from playwright.sync_api import sync_playwright
import time
import json

def extract_market_values(player_url: str):
    """Extract all market value data points."""
    
    market_value_url = player_url.replace('/profil/', '/marktwertverlauf/')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to: {market_value_url}")
        page.goto(market_value_url, wait_until='networkidle')
        time.sleep(3)
        
        # Try multiple selector approaches
        print("\n=== Trying different selectors ===")
        
        # Approach 1: All image elements in SVG
        icons1 = page.query_selector_all('svg image')
        print(f"Approach 1 (svg image): Found {len(icons1)} elements")
        
        # Approach 2: Images with href containing 'wappen'
        icons2 = page.query_selector_all('image[href*="wappen"]')
        print(f"Approach 2 (image[href*='wappen']): Found {len(icons2)} elements")
        
        # Approach 3: All images in highcharts container
        icons3 = page.query_selector_all('.highcharts-container image')
        print(f"Approach 3 (.highcharts-container image): Found {len(icons3)} elements")
        
        # Approach 4: Get all images and filter
        all_images = page.query_selector_all('image')
        print(f"Approach 4 (all image elements): Found {len(all_images)} elements")
        
        # Filter for wappen (club badge) images
        wappen_images = []
        for img in all_images:
            href = img.get_attribute('href') or img.get_attribute('xlink:href')
            if href and 'wappen' in href:
                wappen_images.append(img)
        
        print(f"Filtered wappen images: {len(wappen_images)}")
        
        # Use whichever approach found the most icons
        icons = wappen_images if wappen_images else (icons3 if icons3 else (icons2 if icons2 else icons1))
        
        if not icons:
            print("\nNo icons found! Let's dump the page HTML to see what's there...")
            html = page.content()
            # Save first 5000 chars to file
            with open('data/raw/page_debug.html', 'w') as f:
                f.write(html[:10000])
            print("Saved first 10000 chars of HTML to data/raw/page_debug.html")
            
            print("\n\nPress Enter to close browser...")
            input()
            browser.close()
            return []
        
        print(f"\nUsing {len(icons)} icons for extraction")
        market_values = []
        
        for i, icon in enumerate(icons):
            try:
                print(f"\nProcessing icon {i+1}/{len(icons)}...")
                
                # Get icon attributes for debugging
                href = icon.get_attribute('href') or icon.get_attribute('xlink:href')
                x = icon.get_attribute('x')
                y = icon.get_attribute('y')
                print(f"  Icon href: {href}")
                print(f"  Position: x={x}, y={y}")
                
                # Hover over the icon
                icon.hover()
                time.sleep(0.8)  # Longer wait for tooltip
                
                # Try multiple tooltip selectors
                tooltip = (
                    page.query_selector('.highcharts-tooltip') or
                    page.query_selector('[class*="tooltip"]') or
                    page.query_selector('g.highcharts-tooltip')
                )
                
                if tooltip and tooltip.is_visible():
                    tooltip_text = tooltip.inner_text()
                    print(f"  Tooltip: {tooltip_text[:100]}")
                    
                    # Parse tooltip
                    lines = [l.strip() for l in tooltip_text.strip().split('\n') if l.strip()]
                    data_point = {'icon_index': i}
                    
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if any(word in key for word in ['date', 'datum']):
                                data_point['date'] = value
                            elif any(word in key for word in ['market', 'marktwert', 'value', 'wert']):
                                data_point['value_raw'] = value
                                # Try to parse numeric value
                                try:
                                    value_clean = value.replace('€', '').replace(',', '').strip()
                                    if 'm' in value_clean.lower():
                                        data_point['value_millions'] = float(value_clean.lower().replace('m', ''))
                                    elif 'k' in value_clean.lower():
                                        data_point['value_millions'] = float(value_clean.lower().replace('k', '')) / 1000
                                except:
                                    pass
                            elif any(word in key for word in ['club', 'verein']):
                                data_point['club'] = value
                    
                    if data_point and len(data_point) > 1:  # More than just icon_index
                        market_values.append(data_point)
                        print(f"  ✓ Extracted: {data_point}")
                else:
                    print(f"  ✗ No tooltip found or not visible")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print(f"\n\n=== RESULTS ===")
        print(f"Extracted {len(market_values)} market value data points")
        print(json.dumps(market_values, indent=2))
        
        print("\n\nPress Enter to close browser...")
        input()
        
        browser.close()
        return market_values


if __name__ == '__main__':
    player_url = "https://www.transfermarkt.com/lionel-messi/profil/spieler/28003"
    values = extract_market_values(player_url)
    
    if values:
        with open('data/raw/messi_market_values.json', 'w') as f:
            json.dump(values, f, indent=2)
        print(f"\nSaved {len(values)} data points to data/raw/messi_market_values.json")
    else:
        print("\nNo data extracted")

# Made with Bob
