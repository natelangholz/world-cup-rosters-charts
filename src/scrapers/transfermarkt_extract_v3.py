"""
Extract market value data from Transfermarkt - with proper wait for chart rendering.
"""

from playwright.sync_api import sync_playwright
import time
import json
import re

def extract_market_values(player_url: str):
    """Extract all market value data points by waiting for chart to load."""
    
    market_value_url = player_url.replace('/profil/', '/marktwertverlauf/')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to: {market_value_url}")
        page.goto(market_value_url, wait_until='networkidle')
        
        # Wait for page to fully load
        print("Waiting for chart to load...")
        time.sleep(5)
        
        print("Chart loaded, looking for club icons...")
        
        # Get the page content and search for image elements
        page_content = page.content()
        
        # Find all image elements with wappen (club badge) URLs using regex
        image_pattern = r'<image[^>]*xlink:href="([^"]*wappen[^"]*)"[^>]*x="([^"]*)"[^>]*y="([^"]*)"[^>]*>'
        matches = re.findall(image_pattern, page_content)
        
        print(f"Found {len(matches)} club badge images in HTML")
        
        if not matches:
            print("\nNo images found in HTML. Saving full page content for debugging...")
            with open('data/raw/full_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print("Saved to data/raw/full_page_debug.html")
            
            print("\n\nPress Enter to close browser...")
            input()
            browser.close()
            return []
        
        # Now try to interact with the actual elements
        # Use JavaScript to find and hover over elements
        market_values = []
        
        print("\nAttempting to extract data by hovering over icons...")
        
        for i, (href, x, y) in enumerate(matches):
            try:
                print(f"\nIcon {i+1}/{len(matches)}")
                print(f"  URL: {href}")
                print(f"  Position: x={x}, y={y}")
                
                # Use JavaScript to trigger hover at the specific coordinates
                # Convert x, y to numbers and add offset for center of icon
                x_coord = float(x) + 10  # Center of 20px icon
                y_coord = float(y) + 10
                
                # Find the SVG container and trigger hover
                result = page.evaluate(f"""
                    () => {{
                        // Find all image elements
                        const images = document.querySelectorAll('image');
                        let targetImage = null;
                        
                        // Find the image at approximately this position
                        for (const img of images) {{
                            const x = parseFloat(img.getAttribute('x'));
                            const y = parseFloat(img.getAttribute('y'));
                            if (Math.abs(x - {x}) < 1 && Math.abs(y - {y}) < 1) {{
                                targetImage = img;
                                break;
                            }}
                        }}
                        
                        if (targetImage) {{
                            // Trigger mouseover event
                            const event = new MouseEvent('mouseover', {{
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }});
                            targetImage.dispatchEvent(event);
                            return true;
                        }}
                        return false;
                    }}
                """)
                
                if result:
                    print(f"  ✓ Triggered hover event")
                    time.sleep(1)  # Wait for tooltip
                    
                    # Look for tooltip
                    tooltip = page.query_selector('.highcharts-tooltip')
                    if tooltip and tooltip.is_visible():
                        tooltip_html = tooltip.inner_html()
                        tooltip_text = tooltip.inner_text()
                        
                        print(f"  ✓ Tooltip found:")
                        print(f"    {tooltip_text[:200]}")
                        
                        # Parse the tooltip
                        data_point = {
                            'icon_index': i,
                            'club_badge_url': href
                        }
                        
                        # Extract date (look for patterns like "May 29, 2018" or "29.05.2018")
                        date_patterns = [
                            r'(\w+ \d{1,2}, \d{4})',  # May 29, 2018
                            r'(\d{1,2}\.\d{1,2}\.\d{4})',  # 29.05.2018
                            r'(\d{1,2}/\d{1,2}/\d{4})'  # 29/05/2018
                        ]
                        for pattern in date_patterns:
                            date_match = re.search(pattern, tooltip_text)
                            if date_match:
                                data_point['date'] = date_match.group(1)
                                break
                        
                        # Extract market value (look for €X.XXm or €XXXk)
                        value_match = re.search(r'€\s*([\d.]+)\s*([mk])', tooltip_text, re.IGNORECASE)
                        if value_match:
                            value_num = float(value_match.group(1))
                            unit = value_match.group(2).lower()
                            if unit == 'm':
                                data_point['value_millions'] = value_num
                            elif unit == 'k':
                                data_point['value_millions'] = value_num / 1000
                            data_point['value_raw'] = f"€{value_num}{unit}"
                        
                        # Extract club name (usually after "Club:" or "Verein:")
                        club_match = re.search(r'(?:Club|Verein):\s*([^\n]+)', tooltip_text, re.IGNORECASE)
                        if club_match:
                            data_point['club'] = club_match.group(1).strip()
                        
                        if len(data_point) > 2:  # More than just index and badge URL
                            market_values.append(data_point)
                            print(f"  ✓ Extracted: {data_point}")
                        else:
                            print(f"  ⚠ Could not parse tooltip data")
                    else:
                        print(f"  ✗ No tooltip visible")
                else:
                    print(f"  ✗ Could not trigger hover")
                    
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
