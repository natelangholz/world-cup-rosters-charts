"""
Identify players with wrong IDs by testing API and proposing corrections.
Does NOT modify the dataset - only creates a report.
"""

import pandas as pd
import requests
import time

def test_player_id(player_id):
    """Test if a player ID has market value data."""
    api_url = f"https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history"
    
    try:
        response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        if data.get('success'):
            history = data.get('data', {}).get('history', [])
            return len(history) > 0
        return False
    except:
        return False

def search_player_id(player_name, dob=None):
    """Search for correct player ID."""
    search_url = "https://tmapi-alpha.transfermarkt.technology/search"
    params = {'query': player_name}
    
    try:
        response = requests.get(search_url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        if data.get('success') and data.get('data', {}).get('players'):
            players = data['data']['players']
            
            # If DOB provided, try to match
            if dob and players:
                for player in players:
                    if player.get('dateOfBirth') == dob:
                        return player.get('id'), 'DOB match'
            
            # Return first result
            if players:
                return players[0].get('id'), 'First result'
        
        return None, None
    except:
        return None, None

def main():
    print("=" * 120)
    print("IDENTIFYING WRONG PLAYER IDS")
    print("=" * 120)
    
    df = pd.read_csv('data/processed/rosters_with_market_values.csv')
    df_focus = df[df['Year'] >= 2006].copy()
    missing = df_focus[
        (df_focus['Transfermarkt_ID'].notna()) &
        (df_focus['Market_Value_EUR'].isna())
    ].copy()
    
    print(f"\nTesting {len(missing)} players with IDs but no market values...")
    print("\nThis will:")
    print("  1. Test if current ID has market value data")
    print("  2. If not, search for alternative ID")
    print("  3. Generate report (NO changes to dataset)")
    print("-" * 120)
    
    corrections = []
    
    for i, (idx, row) in enumerate(missing.iterrows(), 1):
        player_id = int(row['Transfermarkt_ID'])
        player_name = row['Player']
        country = row['Country']
        year = int(row['Year'])
        dob = row['DOB']
        
        print(f"\n[{i}/{len(missing)}] {year} - {player_name} ({country}) - Current ID: {player_id}")
        
        # Test current ID
        has_data = test_player_id(str(player_id))
        
        if has_data:
            print(f"  ✓ Current ID has data")
        else:
            print(f"  ✗ Current ID has NO data - searching for alternative...")
            
            new_id, match_type = search_player_id(player_name, dob)
            
            if new_id and new_id != player_id:
                # Test new ID
                new_has_data = test_player_id(str(new_id))
                
                if new_has_data:
                    print(f"  → Proposed ID: {new_id} ({match_type}) - HAS DATA ✓")
                    corrections.append({
                        'Year': year,
                        'Player': player_name,
                        'Country': country,
                        'DOB': dob,
                        'Old_ID': player_id,
                        'New_ID': new_id,
                        'Match_Type': match_type,
                        'New_Has_Data': 'Yes'
                    })
                else:
                    print(f"  → Proposed ID: {new_id} ({match_type}) - NO DATA ✗")
                    corrections.append({
                        'Year': year,
                        'Player': player_name,
                        'Country': country,
                        'DOB': dob,
                        'Old_ID': player_id,
                        'New_ID': new_id,
                        'Match_Type': match_type,
                        'New_Has_Data': 'No'
                    })
            else:
                print(f"  ✗ No alternative ID found")
                corrections.append({
                    'Year': year,
                    'Player': player_name,
                    'Country': country,
                    'DOB': dob,
                    'Old_ID': player_id,
                    'New_ID': None,
                    'Match_Type': 'Not found',
                    'New_Has_Data': 'N/A'
                })
        
        time.sleep(0.5)
    
    # Save report
    if corrections:
        corrections_df = pd.DataFrame(corrections)
        corrections_df.to_csv('data/cache/id_corrections_proposed.csv', index=False)
        
        print("\n" + "=" * 120)
        print("SUMMARY")
        print("=" * 120)
        
        with_new_id = corrections_df[corrections_df['New_ID'].notna()]
        with_data = corrections_df[corrections_df['New_Has_Data'] == 'Yes']
        
        print(f"\nTotal players tested: {len(missing)}")
        print(f"Players needing ID correction: {len(corrections)}")
        print(f"Alternative IDs found: {len(with_new_id)}")
        print(f"Alternative IDs with data: {len(with_data)}")
        
        print(f"\n✓ Report saved to: data/cache/id_corrections_proposed.csv")
        
        if len(with_data) > 0:
            print(f"\nProposed corrections with data:")
            print("-" * 120)
            print(with_data[['Year', 'Player', 'Country', 'Old_ID', 'New_ID', 'Match_Type']].to_string(index=False))

if __name__ == '__main__':
    main()

# Made with Bob
