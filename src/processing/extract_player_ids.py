#!/usr/bin/env python3
"""
Extract Transfermarkt player IDs from roster data.
Creates a CSV file with player_id and Player columns for market value scraping.
"""

import pandas as pd
import re
from pathlib import Path

def extract_player_id_from_url(url):
    """Extract player ID from Transfermarkt URL."""
    if pd.isna(url) or not url:
        return None
    
    # Pattern: /spieler/{player_id}
    match = re.search(r'/spieler/(\d+)', str(url))
    if match:
        return match.group(1)
    return None

def main():
    """Extract player IDs from roster data."""
    # Load roster data
    rosters_file = "data/processed/rosters_combined.csv"
    output_file = "data/processed/player_ids.csv"
    
    print(f"Loading rosters from {rosters_file}...")
    df = pd.read_csv(rosters_file)
    
    print(f"Total players: {len(df)}")
    
    # Extract player IDs from Transfermarkt_URL column
    if 'Transfermarkt_URL' in df.columns:
        print("Extracting player IDs from Transfermarkt_URL column...")
        df['player_id'] = df['Transfermarkt_URL'].apply(extract_player_id_from_url)
    else:
        print("❌ Error: Transfermarkt_URL column not found in roster data")
        return
    
    # Get unique players with IDs
    players_with_ids = df[df['player_id'].notna()][['player_id', 'Player']].drop_duplicates()
    
    print(f"\nPlayers with Transfermarkt IDs: {len(players_with_ids)}")
    print(f"Players without IDs: {len(df) - df['player_id'].notna().sum()}")
    
    # Save to CSV
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    players_with_ids.to_csv(output_file, index=False)
    
    print(f"\n✅ Saved player IDs to {output_file}")
    
    # Show sample
    print(f"\nSample of player IDs:")
    print(players_with_ids.head(10).to_string(index=False))

if __name__ == "__main__":
    main()

# Made with Bob
