"""
Intercept network requests to find Transfermarkt's API endpoint for market value data.
"""

from playwright.sync_api import sync_playwright
import json
import time

def intercept_network_requests(player_url: str):
    """
    Monitor all network requests to find the API endpoint that provides market value data.
    """
    
    market_value_url = player_url.replace('/profil/', '/marktwertverlauf/')
    
    # Store all requests
    requests_log = []
    responses_log = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Set up request/response logging
        def log_request(request):
            requests_log.append({
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data
            })
            print(f"REQUEST: {request.method} {request.url}")
        
        def log_response(response):
            url = response.url
            status = response.status
            
            # Only log interesting responses
            if any(keyword in url.lower() for keyword in ['api', 'ajax', 'json', 'data', 'chart', 'markt', 'wert']):
                print(f"\n🔍 INTERESTING RESPONSE: {status} {url}")
                
                try:
                    # Try to get response body
                    body = response.body()
                    
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(body)
                        print(f"   JSON Response (first 500 chars):")
                        print(f"   {json.dumps(json_data, indent=2)[:500]}")
                        
                        responses_log.append({
                            'url': url,
                            'status': status,
                            'json': json_data
                        })
                    except:
                        # Not JSON, show first 200 chars
                        text = body.decode('utf-8', errors='ignore')
                        print(f"   Text Response (first 200 chars):")
                        print(f"   {text[:200]}")
                        
                        responses_log.append({
                            'url': url,
                            'status': status,
                            'text': text[:500]
                        })
                except Exception as e:
                    print(f"   Could not read response body: {e}")
        
        # Attach listeners
        page.on('request', log_request)
        page.on('response', log_response)
        
        print(f"\n{'='*80}")
        print(f"Navigating to: {market_value_url}")
        print(f"{'='*80}\n")
        
        page.goto(market_value_url, wait_until='networkidle')
        
        print(f"\n{'='*80}")
        print("Page loaded. Waiting 5 seconds for any delayed requests...")
        print(f"{'='*80}\n")
        
        time.sleep(5)
        
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total requests: {len(requests_log)}")
        print(f"Interesting responses: {len(responses_log)}")
        
        # Save logs
        with open('data/raw/network_requests.json', 'w') as f:
            json.dump(requests_log, f, indent=2)
        
        with open('data/raw/network_responses.json', 'w') as f:
            json.dump(responses_log, f, indent=2)
        
        print(f"\nSaved logs to:")
        print(f"  - data/raw/network_requests.json")
        print(f"  - data/raw/network_responses.json")
        
        print(f"\n{'='*80}")
        print("Press Enter to close browser and see detailed analysis...")
        print(f"{'='*80}\n")
        input()
        
        # Analyze responses for market value data
        print(f"\n{'='*80}")
        print("ANALYZING RESPONSES FOR MARKET VALUE DATA")
        print(f"{'='*80}\n")
        
        for i, resp in enumerate(responses_log):
            print(f"\nResponse {i+1}:")
            print(f"  URL: {resp['url']}")
            print(f"  Status: {resp['status']}")
            
            if 'json' in resp:
                # Look for market value patterns in JSON
                json_str = json.dumps(resp['json']).lower()
                if any(keyword in json_str for keyword in ['market', 'wert', 'value', 'datum', 'date']):
                    print(f"  ✓ Contains market value keywords!")
                    print(f"  Full JSON:")
                    print(json.dumps(resp['json'], indent=2))
        
        browser.close()
        
        return responses_log


if __name__ == '__main__':
    player_url = "https://www.transfermarkt.com/lionel-messi/profil/spieler/28003"
    responses = intercept_network_requests(player_url)
    
    print(f"\n\nFound {len(responses)} interesting responses")
    print("Check the JSON files for detailed information")

# Made with Bob
