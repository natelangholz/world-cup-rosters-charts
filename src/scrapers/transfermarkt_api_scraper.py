#!/usr/bin/env python3
"""
Scrape player market values from Transfermarkt API.
API endpoint: https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history
"""

import asyncio
import json
import pandas as pd
from pathlib import Path
import aiohttp
from datetime import datetime
import time

# World Cup dates for matching market values
WORLD_CUP_DATES = {
    1998: "1998-06-10",  # Start of 1998 World Cup
    2002: "2002-05-31",  # Start of 2002 World Cup
    2006: "2006-06-09",  # Start of 2006 World Cup
    2010: "2010-06-11",  # Start of 2010 World Cup
    2014: "2014-06-12",  # Start of 2014 World Cup
    2018: "2018-06-14",  # Start of 2018 World Cup
    2022: "2022-11-20",  # Start of 2022 World Cup
    2026: "2026-06-11",  # Estimated start of 2026 World Cup
}

API_BASE = "https://tmapi-alpha.transfermarkt.technology"

async def fetch_player_market_value(session, player_id, player_name, retries=3):
    """Fetch market value history for a single player."""
    url = f"{API_BASE}/player/{player_id}/market-value-history"
    
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        return {
                            "player_id": player_id,
                            "player_name": player_name,
                            "history": data["data"]["history"]
                        }
                    else:
                        print(f"  ❌ API returned success=false for {player_name} ({player_id})")
                        return None
                elif response.status == 404:
                    print(f"  ⚠️  Player not found: {player_name} ({player_id})")
                    return None
                else:
                    print(f"  ⚠️  HTTP {response.status} for {player_name} ({player_id})")
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
        except Exception as e:
            print(f"  ❌ Error fetching {player_name} ({player_id}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            continue
    
    return None

def find_closest_market_value(history, target_date):
    """Find the market value closest to (but before) the target date."""
    if not history:
        return None
    
    target = datetime.strptime(target_date, "%Y-%m-%d")
    closest = None
    closest_diff = float('inf')
    
    for entry in history:
        determined = datetime.strptime(entry["marketValue"]["determined"], "%Y-%m-%d")
        diff = (target - determined).days
        
        # Only consider values determined before or on the target date
        if 0 <= diff < closest_diff:
            closest_diff = diff
            closest = entry
    
    return closest

async def scrape_market_values(player_ids_file, output_file, batch_size=50, delay=0.1, year=None, country=None):
    """
    Scrape market values for all players or filter by year/country.
    
    Args:
        player_ids_file: CSV file with player_id and player_name columns
        output_file: Output JSON file for raw market value data
        batch_size: Number of concurrent requests
        delay: Delay between batches (seconds)
        year: (optional) Filter to specific World Cup year
        country: (optional) Filter to specific country
    """
    # Load player IDs
    print(f"Loading player IDs from {player_ids_file}...")
    
    # Check if it's JSON or CSV
    if player_ids_file.endswith('.json'):
        import json
        with open(player_ids_file, 'r') as f:
            player_data = json.load(f)
        df = pd.DataFrame(player_data)
    else:
        df = pd.read_csv(player_ids_file)
    
    if 'player_id' not in df.columns:
        print("❌ Error: player_ids_file must have 'player_id' column")
        return
    
    # Apply filters if specified
    if year is not None:
        if 'year' in df.columns:
            df = df[df['year'] == year]
            print(f"Filtering to year {year}")
    
    if country is not None:
        if 'country' in df.columns:
            df = df[df['country'] == country]
            print(f"Filtering to country {country}")
    
    # Get unique players (use 'name' column from JSON or CSV)
    name_col = 'name' if 'name' in df.columns else 'Player'
    players = df[['player_id', name_col]].drop_duplicates()
    players.columns = ['player_id', 'Player']  # Rename for consistency
    print(f"Found {len(players)} unique players")
    
    # Create output directory
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Fetch market values
    results = []
    total = len(players)
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, total, batch_size):
            batch = players.iloc[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({i+1}-{min(i+batch_size, total)}/{total})")
            
            tasks = [
                fetch_player_market_value(session, row['player_id'], row['Player'])
                for _, row in batch.iterrows()
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend([r for r in batch_results if r is not None])
            
            print(f"  ✓ Fetched {len([r for r in batch_results if r is not None])}/{len(batch)} successfully")
            
            # Rate limiting
            if i + batch_size < total:
                await asyncio.sleep(delay)
    
    # Save raw results
    print(f"\n💾 Saving raw market value data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Scraped market values for {len(results)}/{total} players")
    return results

def process_market_values(raw_data_file, rosters_file, player_ids_file, output_file):
    """
    Process raw market value data and match to World Cup rosters.
    
    Args:
        raw_data_file: JSON file with raw market value history
        rosters_file: CSV file with World Cup rosters
        player_ids_file: JSON file with player IDs
        output_file: Output CSV file with market values added
    """
    print(f"\n📊 Processing market values...")
    
    # Load raw data
    with open(raw_data_file, 'r') as f:
        raw_data = json.load(f)
    
    # Create lookup dictionary
    player_data = {item['player_id']: item['history'] for item in raw_data}
    
    # Load player IDs
    with open(player_ids_file, 'r') as f:
        player_ids_data = json.load(f)
    
    # Create player name to ID mapping
    player_id_map = {}
    for item in player_ids_data:
        if item.get('player_id'):
            # Use original_name for matching
            name = item.get('original_name', item.get('name', ''))
            country = item.get('country', '')
            dob = item.get('dob', '')
            key = (name, country, dob)
            player_id_map[key] = item['player_id']
    
    print(f"  Loaded {len(player_id_map)} player ID mappings")
    
    # Load rosters
    df = pd.read_csv(rosters_file)
    
    # Add player_id column by matching
    df['player_id'] = None
    for idx, row in df.iterrows():
        key = (row['Player'], row['Country'], str(row['DOB']))
        if key in player_id_map:
            df.at[idx, 'player_id'] = player_id_map[key]
    
    matched = df['player_id'].notna().sum()
    print(f"  Matched {matched}/{len(df)} players to IDs ({matched/len(df)*100:.1f}%)")
    
    # Add market value columns
    df['Market_Value_EUR'] = None
    df['Market_Value_Date'] = None
    df['Market_Value_Age'] = None
    
    # Match market values to World Cup dates
    matched_values = 0
    for idx, row in df.iterrows():
        if pd.isna(row['player_id']):
            continue
            
        player_id = str(int(row['player_id']))
        year = row['Year']
        
        if player_id in player_data and year in WORLD_CUP_DATES:
            target_date = WORLD_CUP_DATES[year]
            closest = find_closest_market_value(player_data[player_id], target_date)
            
            if closest:
                df.at[idx, 'Market_Value_EUR'] = closest['marketValue']['value']
                df.at[idx, 'Market_Value_Date'] = closest['marketValue']['determined']
                df.at[idx, 'Market_Value_Age'] = closest['age']
                matched_values += 1
    
    print(f"  Matched market values for {matched_values} players")
    
    # Save processed data
    df.to_csv(output_file, index=False)
    
    # Print statistics
    total = len(df)
    with_values = df['Market_Value_EUR'].notna().sum()
    print(f"\n📈 Statistics:")
    print(f"  Total players: {total}")
    print(f"  With market values: {with_values} ({with_values/total*100:.1f}%)")
    print(f"  Missing values: {total - with_values} ({(total-with_values)/total*100:.1f}%)")
    
    # By year
    print(f"\n  By World Cup year:")
    for year in sorted(df['Year'].unique()):
        year_df = df[df['Year'] == year]
        year_total = len(year_df)
        year_with = year_df['Market_Value_EUR'].notna().sum()
        print(f"    {year}: {year_with}/{year_total} ({year_with/year_total*100:.1f}%)")
    
    print(f"\n✅ Saved processed data to {output_file}")

async def main():
    """Main function."""
    # File paths
    player_ids_file = "data/processed/player_ids_searched.json"
    raw_output = "data/raw/market_values_raw.json"
    rosters_file = "data/processed/rosters_combined.csv"
    final_output = "data/processed/rosters_with_market_values.csv"
    
    # Step 1: Scrape market values
    print("=" * 80)
    print("STEP 1: Scraping Market Values from Transfermarkt API")
    print("=" * 80)
    
    results = await scrape_market_values(
        player_ids_file=player_ids_file,
        output_file=raw_output,
        batch_size=50,  # Adjust based on API rate limits
        delay=0.1  # Delay between batches
    )
    
    # Step 2: Process and match to rosters
    print("\n" + "=" * 80)
    print("STEP 2: Processing Market Values and Matching to Rosters")
    print("=" * 80)
    
    process_market_values(
        raw_data_file=raw_output,
        rosters_file=rosters_file,
        player_ids_file=player_ids_file,
        output_file=final_output
    )
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
