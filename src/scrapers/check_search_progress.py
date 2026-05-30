#!/usr/bin/env python3
"""Quick script to check player search progress."""

import json
from pathlib import Path

def check_progress():
    file_path = "data/processed/player_ids_searched.json"
    
    if not Path(file_path).exists():
        print("No progress file found yet")
        return
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    total_target = 4885
    current = len(data)
    found = sum(1 for p in data if p.get('player_id'))
    not_found = current - found
    
    print(f"Player ID Search Progress")
    print(f"=" * 50)
    print(f"Searched: {current}/{total_target} ({current/total_target*100:.1f}%)")
    print(f"Found IDs: {found} ({found/current*100:.1f}%)")
    print(f"Not found: {not_found} ({not_found/current*100:.1f}%)")
    print(f"Remaining: {total_target - current}")
    
    if current > 0:
        # Estimate time remaining (rough estimate based on ~0.5s per player)
        remaining = total_target - current
        est_minutes = (remaining * 0.5) / 60
        print(f"Estimated time remaining: {est_minutes:.0f} minutes ({est_minutes/60:.1f} hours)")

if __name__ == "__main__":
    check_progress()

# Made with Bob
