"""
Wikipedia World Cup Squad Scraper

Scrapes FIFA World Cup squad data from Wikipedia pages.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from bs4 import BeautifulSoup, Tag

from .utils import (
    fetch_with_retry,
    parse_html,
    respectful_delay,
    standardize_position,
    clean_player_name,
    extract_number_from_text,
    save_to_csv,
    get_country_code,
    logger
)

# World Cup years to scrape
WORLD_CUP_YEARS = [1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]

# CSV field names
FIELDNAMES = [
    'Country',
    'Number',
    'Position',
    'Player',
    'DOB',
    'Age',
    'Caps',
    'Club',
    'Club_Country',
    'Home_Country_Flag',
    'Year'
]


class WikipediaSquadScraper:
    """Scraper for Wikipedia World Cup squad pages."""
    
    def __init__(self, output_dir: str = 'data/raw/rosters'):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_squad_url(self, year: int) -> str:
        """
        Get the Wikipedia URL for a given World Cup year.
        
        Args:
            year: World Cup year
        
        Returns:
            Wikipedia URL
        """
        return f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads"
    
    def fetch_page(self, year: int) -> BeautifulSoup:
        """
        Fetch and parse a Wikipedia squad page.
        
        Args:
            year: World Cup year
        
        Returns:
            Parsed HTML
        """
        url = self.get_squad_url(year)
        response = fetch_with_retry(url)
        return parse_html(response.content.decode('utf-8'))
    
    def extract_countries(self, soup: BeautifulSoup) -> List[Tuple[str, Tag]]:
        """
        Extract country names and their corresponding sections.
        
        Args:
            soup: Parsed HTML
        
        Returns:
            List of (country_name, section_element) tuples
        """
        countries = []
        
        # Find all wikitable tables (squad tables)
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            # Find the preceding h3 header for this table
            h3 = table.find_previous('h3')
            
            if not h3:
                continue
            
            # Get country name from id attribute or text content
            country_name = None
            if h3.get('id'):
                country_name = h3.get('id').replace('_', ' ')
            else:
                country_name = h3.get_text().strip()
            
            if not country_name:
                continue
            
            # Skip non-country sections
            skip_sections = [
                'Contents', 'References', 'External links', 'See also',
                'Notes', 'Bibliography', 'Further reading', 'Navigation menu',
                'Group'  # Skip group headers
            ]
            if any(skip.lower() in country_name.lower() for skip in skip_sections):
                continue
            
            # Verify this looks like a squad table (has player data)
            first_row = table.find('tr')
            if first_row and ('player' in first_row.get_text().lower() or
                            'pos' in first_row.get_text().lower()):
                countries.append((country_name, table))
                self.logger.debug(f"Found table for {country_name}")
        
        self.logger.info(f"Found {len(countries)} countries")
        return countries
    
    def identify_column_indices(self, header_row: Tag) -> Dict[str, int]:
        """
        Identify column positions in the table header.
        
        Args:
            header_row: Table header row
        
        Returns:
            Dictionary mapping field names to column indices
        """
        columns = {}
        headers = header_row.find_all(['th', 'td'])
        
        for idx, header in enumerate(headers):
            text = header.get_text().strip().lower()
            
            if 'no' in text or '#' in text or text == 'no.':
                columns['number'] = idx
            elif 'pos' in text:
                columns['position'] = idx
            elif 'player' in text or 'name' in text:
                columns['player'] = idx
            elif 'birth' in text or 'dob' in text or 'date of birth' in text:
                columns['dob'] = idx
            elif 'cap' in text:
                columns['caps'] = idx
            elif 'club' in text:
                columns['club'] = idx
        
        self.logger.debug(f"Column indices: {columns}")
        return columns
    
    def extract_dob_and_age(self, cell: Tag) -> Tuple[Optional[str], Optional[int]]:
        """
        Extract date of birth and age from a cell.
        
        Args:
            cell: Table cell containing DOB/age
        
        Returns:
            Tuple of (DOB string, age)
        """
        text = cell.get_text()
        
        # Try to extract DOB in format (YYYY-MM-DD)
        dob_pattern = r'\((\d{4}-\d{2}-\d{2})\)'
        dob_match = re.search(dob_pattern, text)
        dob = dob_match.group(1) if dob_match else None
        
        # If no ISO format, try other formats
        if not dob:
            # Try format: "15 May 1990"
            date_pattern = r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})'
            date_match = re.search(date_pattern, text)
            if date_match:
                try:
                    day, month, year = date_match.groups()
                    date_obj = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
                    dob = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        
        # Extract age
        age_pattern = r'age[d]?\s+(\d+)'
        age_match = re.search(age_pattern, text, re.IGNORECASE)
        age = int(age_match.group(1)) if age_match else None
        
        return dob, age
    
    def extract_club_info(self, cell: Tag) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract club name and club country from a cell.
        
        Args:
            cell: Table cell containing club info
        
        Returns:
            Tuple of (club_name, club_country)
        """
        club_name = None
        club_country = None
        
        # Try to get club from link
        # Note: Club cells often have multiple links (flag image link + club name link)
        # We need to find the link with actual text (not the flag image link)
        links = cell.find_all('a')
        if links:
            # Find the first link with non-empty text
            for link in links:
                text = link.get_text().strip()
                if text:
                    club_name = text
                    break
        
        # Fallback to cell text if no link found
        if not club_name:
            club_name = cell.get_text().strip()
        
        # Try to get country from flag image
        img = cell.find('img')
        if img and 'alt' in img.attrs:
            club_country = img['alt'].strip()
        
        # Alternative: look for span with flag
        flag_span = cell.find('span', class_='flagicon')
        if flag_span and not club_country:
            flag_img = flag_span.find('img')
            if flag_img and 'alt' in flag_img.attrs:
                club_country = flag_img['alt'].strip()
        
        return club_name, club_country
    
    def parse_squad_table(
        self,
        table: Tag,
        country: str,
        year: int
    ) -> List[Dict[str, any]]:
        """
        Parse a squad table and extract player data.
        
        Args:
            table: Table element
            country: Country name
            year: World Cup year
        
        Returns:
            List of player dictionaries
        """
        players = []
        
        # Find header row
        header_row = table.find('tr')
        if not header_row:
            self.logger.warning(f"No header row found for {country}")
            return players
        
        # Identify column positions
        columns = self.identify_column_indices(header_row)
        
        # Parse data rows
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 4:  # Minimum expected columns
                continue
            
            try:
                # Extract number
                number = None
                if 'number' in columns:
                    number_text = cells[columns['number']].get_text().strip()
                    number = extract_number_from_text(number_text)
                
                # Extract position
                position = None
                if 'position' in columns:
                    position_text = cells[columns['position']].get_text().strip()
                    position = standardize_position(position_text)
                
                # Extract player name
                player_name = None
                if 'player' in columns:
                    player_name = clean_player_name(
                        cells[columns['player']].get_text().strip()
                    )
                
                # Extract DOB and age
                dob, age = None, None
                if 'dob' in columns:
                    dob, age = self.extract_dob_and_age(cells[columns['dob']])
                
                # Extract caps
                caps = None
                if 'caps' in columns:
                    caps_text = cells[columns['caps']].get_text().strip()
                    caps = extract_number_from_text(caps_text)
                
                # Extract club info
                club_name, club_country = None, None
                if 'club' in columns:
                    club_name, club_country = self.extract_club_info(
                        cells[columns['club']]
                    )
                
                # Determine if home country flag
                home_country_flag = False
                if club_country:
                    # Normalize country names for comparison
                    home_country_flag = (
                        club_country.lower() == country.lower() or
                        get_country_code(club_country) == get_country_code(country)
                    )
                
                # Create player record
                player_data = {
                    'Country': country,
                    'Number': number,
                    'Position': position,
                    'Player': player_name,
                    'DOB': dob,
                    'Age': age,
                    'Caps': caps,
                    'Club': club_name,
                    'Club_Country': club_country,
                    'Home_Country_Flag': home_country_flag,
                    'Year': year
                }
                
                # Only add if we have at least player name and position
                if player_name and position:
                    players.append(player_data)
                else:
                    self.logger.warning(
                        f"Skipping incomplete record: {player_data}"
                    )
            
            except Exception as e:
                self.logger.error(f"Error parsing row for {country}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(players)} players for {country}")
        return players
    
    def scrape_year(self, year: int) -> List[Dict[str, any]]:
        """
        Scrape all squads for a given World Cup year.
        
        Args:
            year: World Cup year
        
        Returns:
            List of all player records
        """
        self.logger.info(f"Scraping {year} World Cup squads...")
        
        # Fetch page
        soup = self.fetch_page(year)
        
        # Extract countries and tables
        countries = self.extract_countries(soup)
        
        all_players = []
        
        for country_name, table in countries:
            self.logger.info(f"Processing {country_name}...")
            
            players = self.parse_squad_table(table, country_name, year)
            all_players.extend(players)
            
            # Be respectful with delays
            respectful_delay(1.0, 2.0)
        
        self.logger.info(
            f"Scraped {len(all_players)} total players for {year}"
        )
        
        return all_players
    
    def save_year_data(self, year: int, players: List[Dict[str, any]]) -> None:
        """
        Save scraped data for a year to CSV.
        
        Args:
            year: World Cup year
            players: List of player records
        """
        output_file = self.output_dir / f'rosters_{year}.csv'
        save_to_csv(players, output_file, FIELDNAMES)
    
    def scrape_all_years(self, years: Optional[List[int]] = None) -> None:
        """
        Scrape all World Cup years.
        
        Args:
            years: List of years to scrape (default: all years)
        """
        if years is None:
            years = WORLD_CUP_YEARS
        
        for year in years:
            try:
                players = self.scrape_year(year)
                self.save_year_data(year, players)
                
                # Longer delay between years
                if year != years[-1]:
                    respectful_delay(3.0, 5.0)
            
            except Exception as e:
                self.logger.error(f"Failed to scrape {year}: {e}")
                continue


def main():
    """Main entry point for the scraper."""
    scraper = WikipediaSquadScraper()
    
    # Scrape all years
    scraper.scrape_all_years()
    
    logger.info("Scraping complete!")


if __name__ == '__main__':
    main()

# Made with Bob
