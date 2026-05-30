#!/usr/bin/env python3
"""
Extract market value data from Transfermarkt HTML page.
The data is embedded in the HTML and passed to the Svelte component.
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

async def extract_market_value_data(player_url: str):
    """Extract market value data from the HTML page."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"Navigating to: {player_url}")
        await page.goto(player_url, wait_until="networkidle")
        
        # Wait for the chart to load
        await page.wait_for_timeout(3000)
        
        # Get the full HTML content
        html_content = await page.content()
        
        # Save HTML for inspection
        with open('data/raw/transfermarkt_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Saved HTML to data/raw/transfermarkt_page.html")
        
        # Try to find data in various formats
        
        # 1. Look for JSON data in script tags
        print("\n=== Searching for JSON data in script tags ===")
        scripts = await page.query_selector_all('script')
        for i, script in enumerate(scripts):
            content = await script.inner_text()
            if 'market' in content.lower() or 'wert' in content.lower():
                print(f"\nScript {i} contains market/wert keywords:")
                print(content[:500])
        
        # 2. Look for data attributes on elements
        print("\n=== Searching for data attributes ===")
        elements_with_data = await page.query_selector_all('[data-*]')
        print(f"Found {len(elements_with_data)} elements with data attributes")
        
        for elem in elements_with_data[:10]:  # Check first 10
            attrs = await elem.evaluate('el => Array.from(el.attributes).map(a => ({name: a.name, value: a.value}))')
            data_attrs = [a for a in attrs if a['name'].startswith('data-')]
            if data_attrs:
                print(f"Element: {await elem.evaluate('el => el.tagName')}")
                for attr in data_attrs:
                    print(f"  {attr['name']}: {attr['value'][:100]}")
        
        # 3. Try to access the Svelte component's data
        print("\n=== Trying to access Svelte component data ===")
        try:
            # Look for the chart container
            chart_container = await page.query_selector('.market-value-development-graph-extended')
            if chart_container:
                print("Found chart container!")
                # Try to get its data
                data = await chart_container.evaluate('''el => {
                    // Try to access Svelte component data
                    if (el.__svelte) return el.__svelte;
                    if (el._svelte) return el._svelte;
                    return null;
                }''')
                if data:
                    print("Found Svelte data:", json.dumps(data, indent=2)[:500])
        except Exception as e:
            print(f"Error accessing Svelte data: {e}")
        
        # 4. Try to execute JavaScript to get the chart data
        print("\n=== Trying to access Highcharts data ===")
        try:
            chart_data = await page.evaluate('''() => {
                // Highcharts stores chart instances
                if (window.Highcharts && window.Highcharts.charts) {
                    const charts = window.Highcharts.charts.filter(c => c);
                    if (charts.length > 0) {
                        return charts.map(chart => ({
                            series: chart.series.map(s => ({
                                name: s.name,
                                data: s.data.map(point => ({
                                    x: point.x,
                                    y: point.y,
                                    category: point.category
                                }))
                            }))
                        }));
                    }
                }
                return null;
            }''')
            
            if chart_data:
                print("Found Highcharts data!")
                print(json.dumps(chart_data, indent=2))
                
                # Save to file
                with open('data/raw/market_value_chart_data.json', 'w') as f:
                    json.dump(chart_data, f, indent=2)
                print("Saved chart data to data/raw/market_value_chart_data.json")
            else:
                print("No Highcharts data found")
        except Exception as e:
            print(f"Error accessing Highcharts: {e}")
        
        # 5. Search HTML for specific patterns
        print("\n=== Searching HTML for data patterns ===")
        
        # Look for dates and values in specific format
        date_value_pattern = r'(\d{4}-\d{2}-\d{2})["\s,]+(\d+\.?\d*)'
        matches = re.findall(date_value_pattern, html_content)
        if matches:
            print(f"Found {len(matches)} date-value pairs:")
            for date, value in matches[:10]:
                print(f"  {date}: {value}")
        
        # Look for club badges (which indicate data points)
        badge_pattern = r'wappen/medium/(\d+)\.png["\s]+x="([\d.]+)"["\s]+y="([\d.]+)"'
        badge_matches = re.findall(badge_pattern, html_content)
        if badge_matches:
            print(f"\nFound {len(badge_matches)} club badge positions:")
            for club_id, x, y in badge_matches[:10]:
                print(f"  Club {club_id}: x={x}, y={y}")
        
        print("\n=== Keeping browser open for manual inspection ===")
        print("Press Enter to close browser...")
        input()
        
        await browser.close()

async def main():
    # Test with Lionel Messi
    player_url = "https://www.transfermarkt.com/lionel-messi/marktwertverlauf/spieler/28003"
    await extract_market_value_data(player_url)

if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
