"""
Data cleaning and processing for World Cup roster data.
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RosterDataCleaner:
    """Clean and process World Cup roster data."""
    
    def __init__(self, raw_data_dir: str = 'data/raw/rosters'):
        """
        Initialize the data cleaner.
        
        Args:
            raw_data_dir: Directory containing raw CSV files
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.df = None
    
    def load_all_years(self) -> pd.DataFrame:
        """
        Load all roster CSV files and combine them.
        
        Returns:
            Combined DataFrame
        """
        dfs = []
        
        for csv_file in sorted(self.raw_data_dir.glob('rosters_*.csv')):
            logger.info(f"Loading {csv_file.name}")
            df = pd.read_csv(csv_file)
            dfs.append(df)
        
        self.df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Loaded {len(self.df)} total records")
        
        return self.df
    
    def clean_position(self) -> None:
        """Clean position field - remove number prefixes."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        # Remove number prefixes like "1GK", "2DF", etc.
        self.df['Position'] = self.df['Position'].astype(str).apply(
            lambda x: re.sub(r'^\d+', '', x).strip()
        )
        
        # Standardize any remaining variations
        position_map = {
            'GK': 'GK',
            'DF': 'DF',
            'MF': 'MF',
            'FW': 'FW',
        }
        
        self.df['Position'] = self.df['Position'].map(
            lambda x: position_map.get(x, x) if pd.notna(x) else x
        )
        
        logger.info("Cleaned position field")
    
    def clean_club_country(self) -> None:
        """Clean club country field - convert federation names to country names."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        # Mapping of federation names to country names
        federation_to_country = {
            'The Football Association': 'England',
            'Royal Spanish Football Federation': 'Spain',
            'German Football Association': 'Germany',
            'Italian Football Federation': 'Italy',
            'French Football Federation': 'France',
            'Royal Dutch Football Association': 'Netherlands',
            'Portuguese Football Federation': 'Portugal',
            'Royal Belgian Football Association': 'Belgium',
            'Turkish Football Federation': 'Turkey',
            'Brazilian Football Confederation': 'Brazil',
            'Argentine Football Association': 'Argentina',
            'Mexican Football Federation': 'Mexico',
            'United States Soccer Federation': 'United States',
            'Ecuadorian Football Federation': 'Ecuador',
            'Colombian Football Federation': 'Colombia',
            'Chilean Football Federation': 'Chile',
            'Uruguayan Football Association': 'Uruguay',
            'Peruvian Football Federation': 'Peru',
            'Venezuelan Football Federation': 'Venezuela',
            'Saudi Arabian Football Federation': 'Saudi Arabia',
            'Japan Football Association': 'Japan',
            'Korea Football Association': 'South Korea',
            'Football Association of Thailand': 'Thailand',
            'All India Football Federation': 'India',
            'Chinese Football Association': 'China',
            'Australian Football Confederation': 'Australia',
            'Football Federation Australia': 'Australia',
            'Swiss Football Association': 'Switzerland',
            'Austrian Football Association': 'Austria',
            'Royal Swedish Football Association': 'Sweden',
            'Danish Football Association': 'Denmark',
            'Norwegian Football Federation': 'Norway',
            'Polish Football Association': 'Poland',
            'Czech Football Association': 'Czech Republic',
            'Croatian Football Federation': 'Croatia',
            'Serbian Football Association': 'Serbia',
            'Ukrainian Football Association': 'Ukraine',
            'Russian Football Union': 'Russia',
            'Scottish Football Association': 'Scotland',
            'Football Association of Wales': 'Wales',
            'Football Association of Ireland': 'Republic of Ireland',
            'Royal Moroccan Football Federation': 'Morocco',
            'Egyptian Football Association': 'Egypt',
            'Nigerian Football Federation': 'Nigeria',
            'Ghanaian Football Association': 'Ghana',
            'South African Football Association': 'South Africa',
            'Cameroonian Football Federation': 'Cameroon',
            'Senegalese Football Federation': 'Senegal',
            'Tunisian Football Federation': 'Tunisia',
            'Algerian Football Federation': 'Algeria',
            'Ivorian Football Federation': 'Ivory Coast',
        }
        
        # Apply mapping
        self.df['Club_Country'] = self.df['Club_Country'].replace(
            federation_to_country
        )
        
        logger.info("Cleaned club country field")
    
    def recalculate_home_country_flag(self) -> None:
        """Recalculate Home_Country_Flag after cleaning club countries."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        self.df['Home_Country_Flag'] = (
            self.df['Country'].str.lower() == self.df['Club_Country'].str.lower()
        )
        
        logger.info("Recalculated home country flags")
    
    def add_previous_world_cups(self) -> None:
        """
        Add a field showing how many previous World Cups each player participated in.
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        # Sort by year to ensure chronological order
        self.df = self.df.sort_values(['Year', 'Country', 'Player'])
        
        # Initialize the new column
        self.df['Previous_World_Cups'] = 0
        
        # Group by player name and calculate previous appearances
        player_appearances = {}
        
        for idx, row in self.df.iterrows():
            player = row['Player']
            year = row['Year']
            
            if pd.isna(player) or player == '':
                continue
            
            # Get previous appearances for this player
            if player in player_appearances:
                # Count how many years before current year
                previous_years = [y for y in player_appearances[player] if y < year]
                self.df.at[idx, 'Previous_World_Cups'] = len(previous_years)
                
                # Add current year to player's history
                player_appearances[player].append(year)
            else:
                # First appearance
                self.df.at[idx, 'Previous_World_Cups'] = 0
                player_appearances[player] = [year]
        
        logger.info("Added Previous_World_Cups field")
        
        # Log some statistics
        max_appearances = self.df['Previous_World_Cups'].max()
        veterans = self.df[self.df['Previous_World_Cups'] >= 3]
        logger.info(f"Maximum previous World Cups: {max_appearances}")
        logger.info(f"Players with 3+ previous World Cups: {len(veterans)}")
    
    def convert_data_types(self) -> None:
        """Convert columns to appropriate data types."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        # Convert numeric columns
        numeric_columns = ['Number', 'Age', 'Caps', 'Year', 'Previous_World_Cups']
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Convert boolean column
        self.df['Home_Country_Flag'] = self.df['Home_Country_Flag'].astype(bool)
        
        # Convert date column
        self.df['DOB'] = pd.to_datetime(self.df['DOB'], errors='coerce')
        
        logger.info("Converted data types")
    
    def remove_duplicates(self) -> None:
        """Remove duplicate records."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        initial_count = len(self.df)
        
        # Remove exact duplicates
        self.df = self.df.drop_duplicates()
        
        # Remove duplicates based on key fields
        self.df = self.df.drop_duplicates(
            subset=['Country', 'Player', 'Year'],
            keep='first'
        )
        
        removed = initial_count - len(self.df)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate records")
    
    def validate_data(self) -> Dict[str, any]:
        """
        Validate data quality and return statistics.
        
        Returns:
            Dictionary of validation statistics
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_all_years() first.")
        
        stats = {
            'total_records': len(self.df),
            'total_players': self.df['Player'].nunique(),
            'total_countries': self.df['Country'].nunique(),
            'years': sorted(self.df['Year'].unique().tolist()),
            'missing_data': {
                'Player': self.df['Player'].isna().sum(),
                'Position': self.df['Position'].isna().sum(),
                'DOB': self.df['DOB'].isna().sum(),
                'Age': self.df['Age'].isna().sum(),
                'Caps': self.df['Caps'].isna().sum(),
                'Club': self.df['Club'].isna().sum(),
                'Club_Country': self.df['Club_Country'].isna().sum(),
            },
            'position_distribution': self.df['Position'].value_counts().to_dict(),
            'age_stats': {
                'min': self.df['Age'].min(),
                'max': self.df['Age'].max(),
                'mean': self.df['Age'].mean(),
                'median': self.df['Age'].median(),
            },
            'previous_wc_stats': {
                'max': self.df['Previous_World_Cups'].max(),
                'mean': self.df['Previous_World_Cups'].mean(),
                'veterans_3plus': len(self.df[self.df['Previous_World_Cups'] >= 3]),
            }
        }
        
        return stats
    
    def clean_all(self) -> pd.DataFrame:
        """
        Run all cleaning steps in sequence.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning pipeline...")
        
        self.load_all_years()
        self.remove_duplicates()
        self.clean_position()
        self.clean_club_country()
        self.recalculate_home_country_flag()
        self.add_previous_world_cups()
        self.convert_data_types()
        
        logger.info("Data cleaning complete!")
        
        return self.df
    
    def save_cleaned_data(self, output_path: str = 'data/processed/rosters_combined.csv') -> None:
        """
        Save cleaned data to CSV.
        
        Args:
            output_path: Path to save the cleaned data
        """
        if self.df is None:
            raise ValueError("No data to save. Run clean_all() first.")
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_file, index=False)
        logger.info(f"Saved cleaned data to {output_file}")


def main():
    """Main entry point for data cleaning."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cleaner = RosterDataCleaner()
    df = cleaner.clean_all()
    
    # Print validation statistics
    stats = cleaner.validate_data()
    print("\n=== Data Validation Statistics ===")
    print(f"Total records: {stats['total_records']}")
    print(f"Unique players: {stats['total_players']}")
    print(f"Countries: {stats['total_countries']}")
    print(f"Years: {stats['years']}")
    print(f"\nAge statistics:")
    print(f"  Min: {stats['age_stats']['min']}")
    print(f"  Max: {stats['age_stats']['max']}")
    print(f"  Mean: {stats['age_stats']['mean']:.1f}")
    print(f"  Median: {stats['age_stats']['median']}")
    print(f"\nPrevious World Cup statistics:")
    print(f"  Max previous WCs: {stats['previous_wc_stats']['max']}")
    print(f"  Mean previous WCs: {stats['previous_wc_stats']['mean']:.2f}")
    print(f"  Veterans (3+ WCs): {stats['previous_wc_stats']['veterans_3plus']}")
    print(f"\nPosition distribution:")
    for pos, count in stats['position_distribution'].items():
        print(f"  {pos}: {count}")
    
    # Save cleaned data
    cleaner.save_cleaned_data()
    
    print("\nCleaning complete!")


if __name__ == '__main__':
    main()

# Made with Bob
