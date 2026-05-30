"""
Debug script to inspect Transfermarkt market value page structure.
"""

from playwright.sync_api import sync_playwright
import time
import json

def inspect_market_value_page():
    """Inspect the market value page to find where data is stored."""
    
    url = "https://www.transfermarkt.com/lionel-messi/marktwertverlauf/spieler/28003"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to: {url}")
        page.goto(url, wait_until='networkidle')
        time.sleep(3)
        
        # Try to find chart data in various places
        print("\n=== Checking for chart data ===")
        
        # Check window object
        chart_data = page.evaluate("""
            () => {
                const results = {};
                
                // Check common variable names
                if (typeof window.chartData !== 'undefined') results.chartData = window.chartData;
                if (typeof window.marketValueData !== 'undefined') results.marketValueData = window.marketValueData;
                if (typeof window.Highcharts !== 'undefined') {
                    results.hasHighcharts = true;
                    // Try to get chart data from Highcharts
                    if (window.Highcharts.charts && window.Highcharts.charts.length > 0) {
                        results.highchartsData = window.Highcharts.charts[0].series[0].data.map(point => ({
                            x: point.x,
                            y: point.y,
                            name: point.name
                        }));
                    }
                }
                
                // Check for data attributes
                const chartContainer = document.querySelector('.highcharts-container');
                if (chartContainer) {
                    results.hasChartContainer = true;
                }
                
                return results;
            }
        """)
        
        print("Chart data found:")
        print(json.dumps(chart_data, indent=2))
        
        # Try to extract data from the visible table/chart
        print("\n=== Checking for visible data ===")
        
        # Look for data in script tags
        scripts = page.query_selector_all('script')
        for i, script in enumerate(scripts):
            content = script.inner_text()
            if 'marktwertverlauf' in content.lower() or 'market' in content.lower():
                print(f"\n--- Script {i} (first 500 chars) ---")
                print(content[:500])
        
        print("\n\nPress Enter to close browser...")
        input()
        
        browser.close()

if __name__ == '__main__':
    inspect_market_value_page()

# Made with Bob
