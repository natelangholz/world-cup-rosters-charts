#!/usr/bin/env python3
"""
Search for players on Transfermarkt and extract their IDs.
Uses Transfermarkt's search functionality to match player names.
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import re
from pathlib import Path
import json
from datetime import datetime

async def search_player(page, player_name, birth_year=None, nationality=None):
    """
    Search for a player on Transfermarkt and return the best match.
    
    Returns:
        dict with player_id, name, birth_date, nationality, or None if not found
    """
    try:
        # Navigate to search page
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name.replace(' ', '+')}"
        await page.goto(search_url, wait_until="networkidle", timeout=10000)
        
        # Wait a bit for content to load
        await page.wait_for_timeout(1000)
        
        # Check if we got redirected directly to a player page (exact match)
        current_url = page.url
        if '/profil/spieler/' in current_url:
            player_id = re.search(r'/spieler/(\d+)', current_url)
            if player_id:
                return {
                    'player_id': player_id.group(1),
                    'name': player_name,
                    'match_type': 'direct',
                    'url': current_url
                }
        
        # Otherwise, parse search results
        # Look for player results table
        players = await page.query_selector_all('table.items tbody tr')
        
        if not players:
            return None
        
        # Extract info from first result (best match)
        first_player = players[0]
        
        # Get player link
        link = await first_player.query_selector('td.hauptlink a')
        if not link:
            return None
        
        href = await link.get_attribute('href')
        name = await link.inner_text()
        
        player_id = re.search(r'/spieler/(\d+)', href)
        if not player_id:
            return None
        
        # Get birth date if available
        birth_cell = await first_player.query_selector('td.zentriert:nth-child(3)')
        birth_date = await birth_cell.inner_text() if birth_cell else None
        
        # Get nationality
        nat_cell = await first_player.query_selector('td.zentriert img.flaggenrahmen')
        nat_title = await nat_cell.get_attribute('title') if nat_cell else None
        
        return {
            'player_id': player_id.group(1),
            'name': name.strip(),
            'birth_date': birth_date.strip() if birth_date else None,
            'nationality': nat_title,
            'match_type': 'search',
            'url': f"https://www.transfermarkt.com{href}"
        }
        
    except Exception as e:
        print(f"    Error searching for {player_name}: {e}")
        return None

async def search_players_batch(players_df, start_idx=0, batch_size=100):
    """Search for a batch of players."""
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        end_idx = min(start_idx + batch_size, len(players_df))
        
        for idx in range(start_idx, end_idx):
            row = players_df.iloc[idx]
            player_name = row['Player']
            
            print(f"  [{idx+1}/{len(players_df)}] Searching: {player_name}")
            
            result = await search_player(page, player_name)
            
            if result:
                result['original_name'] = player_name
                result['country'] = row.get('Country', '')
                result['dob'] = row.get('DOB', '')
                results.append(result)
                print(f"    > Found: {result['name']} (ID: {result['player_id']})")
            else:
                print(f"    > Not found")
                results.append({
                    'original_name': player_name,
                    'country': row.get('Country', ''),
                    'dob': row.get('DOB', ''),
                    'player_id': None,
                    'match_type': 'not_found'
                })
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        await browser.close()
    
    return results

async def main():
    """Main function to search for all players."""
    # Load roster data
    rosters_file = "data/processed/rosters_combined.csv"
    output_file = "data/processed/player_ids_searched.json"
    
    print("=" * 80)
    print("TRANSFERMARKT PLAYER ID SEARCH")
    print("=" * 80)
    
    print(f"\nLoading rosters from {rosters_file}...")
    df = pd.read_csv(rosters_file)
    
    # Get unique players
    unique_players = df[['Player', 'Country', 'DOB']].drop_duplicates(subset=['Player'])
    print(f"Total unique players: {len(unique_players)}")
    
    # Check if we have partial results
    if Path(output_file).exists():
        print(f"\nFound existing results in {output_file}")
        with open(output_file, 'r') as f:
            existing_results = json.load(f)
        print(f"Already searched: {len(existing_results)} players")
        
        # Find where to resume
        searched_names = {r['original_name'] for r in existing_results}
        remaining = unique_players[~unique_players['Player'].isin(searched_names)]
        print(f"Remaining: {len(remaining)} players")
        
        if len(remaining) == 0:
            print("\nAll players already searched!")
            return
        
        start_idx = len(unique_players) - len(remaining)
        all_results = existing_results
    else:
        start_idx = 0
        all_results = []
    
    # Search in batches
    batch_size = 100
    total = len(unique_players)
    
    print(f"\nStarting search from player {start_idx + 1}...")
    print(f"Batch size: {batch_size}")
    
    for batch_start in range(start_idx, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        print(f"\n{'='*80}")
        print(f"BATCH: Players {batch_start + 1} to {batch_end} of {total}")
        print(f"{'='*80}")
        
        batch_results = await search_players_batch(
            unique_players,
            start_idx=batch_start,
            batch_size=batch_size
        )
        
        all_results.extend(batch_results)
        
        # Save progress after each batch
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\nProgress saved to {output_file}")
        print(f"   Total searched: {len(all_results)}/{total}")
        
        # Summary
        found = sum(1 for r in all_results if r.get('player_id'))
        not_found = len(all_results) - found
        print(f"   Found: {found} ({found/len(all_results)*100:.1f}%)")
        print(f"   Not found: {not_found} ({not_found/len(all_results)*100:.1f}%)")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SEARCH COMPLETE!")
    print(f"{'='*80}")
    
    found = sum(1 for r in all_results if r.get('player_id'))
    not_found = len(all_results) - found
    
    print(f"\nTotal players: {len(all_results)}")
    print(f"Found: {found} ({found/len(all_results)*100:.1f}%)")
    print(f"Not found: {not_found} ({not_found/len(all_results)*100:.1f}%)")
    
    # Create CSV for easy review
    csv_file = "data/processed/player_ids.csv"
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(csv_file, index=False)
    print(f"\nSaved results to:")
    print(f"   JSON: {output_file}")
    print(f"   CSV:  {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
