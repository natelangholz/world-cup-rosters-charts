#!/bin/bash
# World Cup Rosters Project Cleanup Script
# This script organizes the messy src/scrapers directory

set -e

echo "=== World Cup Rosters Project Cleanup ==="
echo ""

# Create archive directories
mkdir -p archive/tests
mkdir -p archive/fixes
mkdir -p archive/deprecated

# Move test files
echo "Moving test files..."
mv src/scrapers/test_*.py archive/tests/ 2>/dev/null || true

# Move one-off fix scripts
echo "Moving one-off fix scripts..."
mv src/scrapers/find_*.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_2026_missing_mv.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_all_missing_mv.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_all_missing_mvs.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_missing_2026_mv.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_mvs_2006_onwards.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fetch_remaining_mv.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fix_all_ids.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fix_and_fetch_all_mv.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fix_ids_from_national_teams.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fix_ids_with_playwright.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/fix_missing_mv_ids.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/auto_fix_ids_from_rosters.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/copy_ids_from_previous_years.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/merge_old_2026_data.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/restore_2026_ids.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/scrape_*.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/search_*.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/update_*.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/verify_and_fix_ids.py archive/fixes/ 2>/dev/null || true
mv src/scrapers/complete_2026_update.py archive/fixes/ 2>/dev/null || true

# Move deprecated versions
echo "Moving deprecated versions..."
mv src/scrapers/transfermarkt_extract.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_extract_v2.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_extract_v3.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_extract_from_html.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_network_intercept.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_debug.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_scraper.py archive/deprecated/ 2>/dev/null || true
mv src/scrapers/transfermarkt_player_search.py archive/deprecated/ 2>/dev/null || true

# Move utility scripts
echo "Moving utility scripts..."
mv src/scrapers/check_*.py archive/fixes/ 2>/dev/null || true

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Core scripts remaining in src/scrapers/:"
ls -1 src/scrapers/*.py 2>/dev/null || echo "  (none)"
echo ""
echo "Archived files:"
echo "  Tests: $(ls -1 archive/tests/*.py 2>/dev/null | wc -l) files"
echo "  Fixes: $(ls -1 archive/fixes/*.py 2>/dev/null | wc -l) files"
echo "  Deprecated: $(ls -1 archive/deprecated/*.py 2>/dev/null | wc -l) files"

# Made with Bob
