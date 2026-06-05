#!/usr/bin/env python3
"""Fix player IDs for any country using Playwright with fuzzy name matching."""

import pandas as pd
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
from difflib import SequenceMatcher

def normalize_name(name: str) -> str:
    name = name.lower().strip()
    for prefix in ['al-', 'el-', 'de ', 'van ', 'von ', 'da ', 'di ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name

def reverse_korean_name(name: str) -> str:
    """Reverse Korean name order: 'Son Heung-min' -> 'Heung-min Son'"""
    parts = name.split()
    if len(parts) >= 2:
        return ' '.join(parts[1:] + [parts[0]])
    return name

def name_similarity(name1: str, name2: str) -> float:
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if norm1 == norm2:
        return 1.0
    if norm1 in norm2 or norm2 in norm1:
        return 0.9
    
    # Try reversed Korean name
    reversed1 = normalize_name(reverse_korean_name(name1))
    if reversed1 == norm2 or reversed1 in norm2 or norm2 in reversed1:
        return 0.95
    
    return max(
        SequenceMatcher(None, norm1, norm2).ratio(),
        SequenceMatcher(None, reversed1, norm2).ratio()
    )

# Country to Transfermarkt team ID mapping
COUNTRY_TEAM_IDS = {
    'South Korea': '3589',
    'Qatar': '3669',
    'Morocco': '3575',
    'Australia': '3436',
    'Ecuador': '3505',
    'Egypt': '3672',
    'Iran': '3582',
    'Saudi Arabia': '3807',
    'Uruguay': '3449',
    'Iraq': '8030',
    'Algeria': '3574',
    'Jordan': '8030',
    'Colombia': '3816',
    'Uzbekistan': '8600',
    'Ghana': '3441',
    'Cape Verde': '3774',
    'New Zealand': '3505',
    'Panama': '3564',
    'Portugal': '3300',
}

def scrape_roster(page, country: str, year: int) -> list:
    team_id = COUNTRY_TEAM_IDS.get(country)
    if not team_id:
        return []
    
    url = f'https://www.transfermarkt.com/a/kader/verein/{team_id}/saison_id/{year}/plus/0'
    
    try:
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        
        roster = []
        rows = page.query_selector_all('table.items tbody tr')
        
        for row in rows:
            try:
                name_cell = row.query_selector('td.hauptlink a')
                if not name_cell:
                    continue
                
                name = name_cell.inner_text().strip()
                href = name_cell.get_attribute('href')
                
                if href and '/profil/spieler/' in href:
                    player_id = href.split('/spieler/')[1].split('/')[0]
                    roster.append({'name': name, 'id': player_id})
            except:
                continue
        
        return roster
    except:
        return []

def find_best_match(player_name: str, roster: list, threshold: float = 0.60):
    best_match = None
    best_score = 0.0
    
    for player in roster:
        score = name_similarity(player_name, player['name'])
        if score > best_score:
            best_score = score
            best_match = player
    
    if best_score >= threshold:
        return best_match, best_score
    return None, best_score

def main():
    parser = argparse.ArgumentParser(description='Fix player IDs using national team rosters')
    parser.add_argument('--country', type=str, help='Specific country to fix')
    parser.add_argument('--year', type=int, help='Specific year to fix')
    parser.add_argument('--all', action='store_true', help='Fix all countries with missing IDs')
    parser.add_argument('--verify', action='store_true', help='Verify and fix wrong IDs (players with IDs but no market values)')
    
    args = parser.parse_args()
    
    data_path = Path('data/processed/rosters_with_market_values.csv')
    df = pd.read_csv(data_path)
    
    # Determine which players to process
    if args.verify:
        # Process players with IDs but no market values
        missing = df[(df['Transfermarkt_ID'].notna()) & (df['Market_Value_EUR'].isna())].copy()
        if args.year:
            missing = missing[missing['Year'] == args.year]
            print(f"Verifying IDs for {args.year} (players with IDs but no market values)")
        elif args.country:
            missing = missing[missing['Country'] == args.country]
            print(f"Verifying IDs for {args.country} (players with IDs but no market values)")
        else:
            print("Verifying all IDs (players with IDs but no market values)")
    elif args.country and args.year:
        missing = df[(df['Country'] == args.country) & (df['Year'] == args.year) & (df['Transfermarkt_ID'].isna())].copy()
        print(f"Processing {args.country} {args.year}")
    elif args.country:
        missing = df[(df['Country'] == args.country) & (df['Transfermarkt_ID'].isna())].copy()
        print(f"Processing all years for {args.country}")
    elif args.year:
        missing = df[(df['Year'] == args.year) & (df['Transfermarkt_ID'].isna())].copy()
        print(f"Processing all countries for {args.year}")
    elif args.all:
        missing = df[df['Transfermarkt_ID'].isna()].copy()
        print("Processing all missing IDs")
    else:
        # Default: South Korea
        missing = df[(df['Country'] == 'South Korea') & (df['Transfermarkt_ID'].isna())].copy()
        print("Processing South Korea (default)")
    
    print("=" * 100)
    print(f"FIXING PLAYER IDS")
    print("=" * 100)
    print(f"\nProcessing {len(missing)} players\n")
    
    stats = {'added': 0, 'failed': 0, 'corrected': 0}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Group by country and year
        for country in sorted(missing['Country'].unique()):
            country_players = missing[missing['Country'] == country]
            
            for year in sorted(country_players['Year'].unique()):
                year_players = country_players[country_players['Year'] == year]
                print(f"\n{country} {year} ({len(year_players)} players)")
                
                roster = scrape_roster(page, country, year)
                if not roster:
                    print("  ✗ No roster")
                    stats['failed'] += len(year_players)
                    continue
                
                print(f"  Found {len(roster)} players in roster")
                
                for _, row in year_players.iterrows():
                    match, score = find_best_match(row['Player'], roster)
                    
                    if match:
                        new_id = int(match['id'])
                        old_id = row.get('Transfermarkt_ID')
                        mask = (df['Year'] == year) & (df['Country'] == country) & (df['Player'] == row['Player'])
                        df.loc[mask, 'Transfermarkt_ID'] = new_id
                        
                        if pd.notna(old_id) and int(old_id) != new_id:
                            print(f"  ✓ {row['Player']:30s} → {match['name']:30s} ID:{int(old_id)}→{new_id} ({score:.2f})")
                            stats['corrected'] += 1
                        else:
                            print(f"  + {row['Player']:30s} → {match['name']:30s} ID:{new_id} ({score:.2f})")
                            stats['added'] += 1
                    else:
                        print(f"  ✗ {row['Player']:30s} No match (best: {score:.2f})")
                        stats['failed'] += 1
                
                time.sleep(1)
        
        browser.close()
    
    # Save
    df.to_csv(data_path, index=False)
    
    print("\n" + "=" * 100)
    print("RESULTS")
    print("=" * 100)
    print(f"Added IDs: {stats['added']}")
    print(f"Corrected IDs: {stats['corrected']}")
    print(f"Failed: {stats['failed']}")
    
    # Final stats by year if specific year requested
    if args.year:
        df_year = df[df['Year'] == args.year]
        coverage = df_year['Transfermarkt_ID'].notna().sum()
        print(f"\n{args.year} ID coverage: {coverage}/{len(df_year)} ({coverage/len(df_year)*100:.1f}%)")
        
        if args.year == 2026 and coverage >= 1233:
            print("✓ TARGET REACHED: 99%+ coverage for 2026!")

if __name__ == '__main__':
    main()

# Made with Bob
