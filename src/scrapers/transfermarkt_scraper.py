"""
Transfermarkt scraper for player market valuations.

This scraper retrieves player market values from Transfermarkt.com
for players in World Cup rosters at the time of each tournament.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TransfermarktScraper:
    """Scraper for Transfermarkt player market valuations."""
    
    BASE_URL = "https://www.transfermarkt.com"
    SEARCH_URL = f"{BASE_URL}/schnellsuche/ergebnis/schnellsuche"
    
    # World Cup dates for historical market value lookups
    WORLD_CUP_DATES = {
        1998: "1998-06-10",
        2002: "2002-05-31",
        2006: "2006-06-09",
        2010: "2010-06-11",
        2014: "2014-06-12",
        2018: "2018-06-14",
        2022: "2022-11-20",
        2026: "2026-06-11"  # Estimated
    }
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        Initialize the scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            delay: Delay between requests in seconds
        """
        self.headless = headless
        self.delay = delay
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def start(self):
        """Start the browser."""
        logger.info("Starting Playwright browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        logger.info("Browser started successfully")
        
    def close(self):
        """Close the browser."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")
        
    def search_player(self, player_name: str, dob: Optional[str] = None) -> Optional[str]:
        """
        Search for a player and return their Transfermarkt profile URL.
        
        Args:
            player_name: Player's full name
            dob: Date of birth in YYYY-MM-DD format (helps with disambiguation)
            
        Returns:
            Player profile URL or None if not found
        """
        try:
            # Navigate to search page
            search_url = f"{self.SEARCH_URL}?query={player_name.replace(' ', '+')}"
            logger.info(f"Searching for player: {player_name}")
            self.page.goto(search_url, wait_until='networkidle')
            time.sleep(self.delay)
            
            # Look for player results
            player_results = self.page.query_selector_all('table.items tbody tr')
            
            if not player_results:
                logger.warning(f"No results found for {player_name}")
                return None
                
            # If DOB provided, try to match it
            if dob:
                for result in player_results:
                    try:
                        result_dob = result.query_selector('td:nth-child(3)')
                        if result_dob and dob in result_dob.inner_text():
                            link = result.query_selector('td:nth-child(2) a')
                            if link:
                                profile_url = self.BASE_URL + link.get_attribute('href')
                                logger.info(f"Found profile for {player_name}: {profile_url}")
                                return profile_url
                    except Exception as e:
                        logger.debug(f"Error checking result: {e}")
                        continue
            
            # If no DOB match or DOB not provided, return first result
            first_result = player_results[0]
            link = first_result.query_selector('td:nth-child(2) a')
            if link:
                profile_url = self.BASE_URL + link.get_attribute('href')
                logger.info(f"Found profile for {player_name}: {profile_url}")
                return profile_url
                
            logger.warning(f"Could not extract profile URL for {player_name}")
            return None
            
        except PlaywrightTimeout:
            logger.error(f"Timeout searching for {player_name}")
            return None
        except Exception as e:
            logger.error(f"Error searching for {player_name}: {e}")
            return None
            
    def get_market_value_at_date(self, profile_url: str, target_date: str) -> Optional[float]:
        """
        Get player's market value at a specific date.
        
        Args:
            profile_url: Player's Transfermarkt profile URL
            target_date: Date in YYYY-MM-DD format
            
        Returns:
            Market value in millions of euros, or None if not available
        """
        try:
            # Navigate to market value page
            market_value_url = profile_url.replace('/profil/', '/marktwertverlauf/')
            logger.info(f"Fetching market value for date {target_date}")
            self.page.goto(market_value_url, wait_until='networkidle')
            time.sleep(self.delay)
            
            # Get market value data from the chart
            # Transfermarkt stores this in a JavaScript variable
            chart_data = self.page.evaluate("""
                () => {
                    if (typeof window.chartData !== 'undefined') {
                        return window.chartData;
                    }
                    return null;
                }
            """)
            
            if not chart_data:
                logger.warning("No market value data found")
                return None
                
            # Parse the data to find value closest to target date
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
            closest_value = None
            min_diff = float('inf')
            
            for entry in chart_data:
                try:
                    entry_date = datetime.strptime(entry['datum_mw'], '%b %d, %Y')
                    diff = abs((entry_date - target_dt).days)
                    
                    if diff < min_diff:
                        min_diff = diff
                        # Value is in the format "€X.XXm" or "€XXXk"
                        value_str = entry['mw']
                        if 'm' in value_str:
                            closest_value = float(value_str.replace('€', '').replace('m', ''))
                        elif 'k' in value_str:
                            closest_value = float(value_str.replace('€', '').replace('k', '')) / 1000
                except Exception as e:
                    logger.debug(f"Error parsing entry: {e}")
                    continue
                    
            if closest_value is not None:
                logger.info(f"Found market value: €{closest_value}m (within {min_diff} days)")
                return closest_value
            else:
                logger.warning("Could not find market value for target date")
                return None
                
        except PlaywrightTimeout:
            logger.error(f"Timeout fetching market value")
            return None
        except Exception as e:
            logger.error(f"Error fetching market value: {e}")
            return None
            
    def scrape_player_value(self, player_name: str, dob: str, year: int) -> Dict:
        """
        Scrape market value for a player at a specific World Cup year.
        
        Args:
            player_name: Player's full name
            dob: Date of birth in YYYY-MM-DD format
            year: World Cup year
            
        Returns:
            Dictionary with player info and market value
        """
        result = {
            'player': player_name,
            'dob': dob,
            'year': year,
            'profile_url': None,
            'market_value_eur': None,
            'value_date': self.WORLD_CUP_DATES.get(year),
            'scraped_at': datetime.now().isoformat()
        }
        
        # Search for player
        profile_url = self.search_player(player_name, dob)
        if not profile_url:
            logger.warning(f"Could not find profile for {player_name}")
            return result
            
        result['profile_url'] = profile_url
        
        # Get market value at World Cup date
        target_date = self.WORLD_CUP_DATES.get(year)
        if not target_date:
            logger.error(f"No World Cup date defined for year {year}")
            return result
            
        market_value = self.get_market_value_at_date(profile_url, target_date)
        result['market_value_eur'] = market_value
        
        return result
        
    def scrape_roster_values(self, roster_df: pd.DataFrame, output_path: str):
        """
        Scrape market values for all players in a roster DataFrame.
        
        Args:
            roster_df: DataFrame with Player, DOB, and Year columns
            output_path: Path to save results CSV
        """
        results = []
        total = len(roster_df)
        
        logger.info(f"Starting to scrape market values for {total} players...")
        
        for idx, row in roster_df.iterrows():
            logger.info(f"Processing {idx + 1}/{total}: {row['Player']}")
            
            result = self.scrape_player_value(
                player_name=row['Player'],
                dob=row['DOB'],
                year=int(row['Year'])
            )
            results.append(result)
            
            # Save progress periodically
            if (idx + 1) % 50 == 0:
                temp_df = pd.DataFrame(results)
                temp_df.to_csv(output_path.replace('.csv', '_temp.csv'), index=False)
                logger.info(f"Saved progress: {idx + 1}/{total} players")
                
        # Save final results
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_path, index=False)
        logger.info(f"Scraping complete! Results saved to {output_path}")
        
        # Print summary statistics
        found = results_df['market_value_eur'].notna().sum()
        logger.info(f"Successfully found market values for {found}/{total} players ({found/total*100:.1f}%)")


def main():
    """Main function for testing the scraper."""
    # Test with a few sample players
    test_data = pd.DataFrame([
        {'Player': 'Lionel Messi', 'DOB': '1987-06-24', 'Year': 2022},
        {'Player': 'Cristiano Ronaldo', 'DOB': '1985-02-05', 'Year': 2022},
        {'Player': 'Kylian Mbappé', 'DOB': '1998-12-20', 'Year': 2022}
    ])
    
    with TransfermarktScraper(headless=False, delay=2.0) as scraper:
        scraper.scrape_roster_values(test_data, 'data/raw/test_market_values.csv')


if __name__ == '__main__':
    main()

# Made with Bob
