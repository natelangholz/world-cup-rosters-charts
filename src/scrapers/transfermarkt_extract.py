"""
Extract market value data from Transfermarkt by simulating hover events.
"""

from playwright.sync_api import sync_playwright
import time
import json

def extract_market_values(player_url: str):
    """
    Extract all market value data points by hovering over chart icons.
    
    Args:
        player_url: Player's Transfermarkt profile URL
        
    Returns:
        List of dicts with date, value, and club info
    """
    
    # Convert profile URL to market value URL
    market_value_url = player_url.replace('/profil/', '/marktwertverlauf/')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to: {market_value_url}")
        page.goto(market_value_url, wait_until='networkidle')
        time.sleep(3)
        
        # Find all club icons in the chart
        icons = page.query_selector_all('svg image[xlink\\:href*="wappen"]')
        print(f"Found {len(icons)} club icons in chart")
        
        market_values = []
        
        for i, icon in enumerate(icons):
            try:
                # Hover over the icon to trigger tooltip
                icon.hover()
                time.sleep(0.5)  # Wait for tooltip to appear
                
                # Try to find the tooltip
                # Highcharts tooltips usually have class 'highcharts-tooltip'
                tooltip = page.query_selector('.highcharts-tooltip')
                
                if tooltip:
                    tooltip_text = tooltip.inner_text()
                    print(f"\nIcon {i+1} tooltip:")
                    print(tooltip_text)
                    
                    # Parse the tooltip text
                    # Format is usually something like:
                    # "Date: May 29, 2018"
                    # "Market value: €180.00m"
                    # "Club: FC Barcelona"
                    
                    lines = tooltip_text.strip().split('\n')
                    data_point = {}
                    
                    for line in lines:
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if 'date' in key or 'datum' in key:
                                data_point['date'] = value
                            elif 'market' in key or 'marktwert' in key or 'value' in key:
                                # Extract numeric value
                                # Remove currency symbols and convert to float
                                value_clean = value.replace('€', '').replace('m', '').replace('k', '').strip()
                                try:
                                    if 'm' in value.lower():
                                        data_point['value_millions'] = float(value_clean)
                                    elif 'k' in value.lower():
                                        data_point['value_millions'] = float(value_clean) / 1000
                                except:
                                    data_point['value_raw'] = value
                            elif 'club' in key or 'verein' in key:
                                data_point['club'] = value
                    
                    if data_point:
                        market_values.append(data_point)
                else:
                    print(f"Icon {i+1}: No tooltip found")
                    
            except Exception as e:
                print(f"Error processing icon {i+1}: {e}")
                continue
        
        print(f"\n\nExtracted {len(market_values)} market value data points")
        print(json.dumps(market_values, indent=2))
        
        print("\n\nPress Enter to close browser...")
        input()
        
        browser.close()
        
        return market_values


if __name__ == '__main__':
    # Test with Messi
    player_url = "https://www.transfermarkt.com/lionel-messi/profil/spieler/28003"
    values = extract_market_values(player_url)
    
    # Save to file
    with open('data/raw/messi_market_values.json', 'w') as f:
        json.dump(values, f, indent=2)
    
    print(f"\nSaved {len(values)} data points to data/raw/messi_market_values.json")

# Made with Bob
