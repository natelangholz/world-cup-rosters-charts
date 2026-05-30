"""
Utility functions for web scraping operations.
"""

import time
import random
import logging
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def get_cache_path(cache_type: str, key: str) -> Path:
    """
    Get the cache file path for a given key.
    
    Args:
        cache_type: Type of cache ('player_searches' or 'market_values')
        key: Cache key (will be hashed)
    
    Returns:
        Path to cache file
    """
    cache_key = hashlib.md5(key.encode()).hexdigest()
    cache_dir = Path(f'data/cache/{cache_type}')
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f'{cache_key}.json'


def get_cached_data(cache_type: str, key: str) -> Optional[Dict[Any, Any]]:
    """
    Retrieve cached data if it exists.
    
    Args:
        cache_type: Type of cache
        key: Cache key
    
    Returns:
        Cached data or None if not found
    """
    cache_file = get_cache_path(cache_type, key)
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                logger.debug(f"Cache hit for {cache_type}: {key}")
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Invalid cache file: {cache_file}")
            return None
    
    logger.debug(f"Cache miss for {cache_type}: {key}")
    return None


def cache_data(cache_type: str, key: str, data: Dict[Any, Any]) -> None:
    """
    Cache data to disk.
    
    Args:
        cache_type: Type of cache
        key: Cache key
        data: Data to cache
    """
    cache_file = get_cache_path(cache_type, key)
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Cached data for {cache_type}: {key}")
    except Exception as e:
        logger.error(f"Failed to cache data: {e}")


def respectful_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> None:
    """
    Add a random delay between requests to be respectful to servers.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)


def rate_limit(calls: int = 10, period: int = 60):
    """
    Decorator to rate limit function calls.
    
    Args:
        calls: Number of calls allowed
        period: Time period in seconds
    """
    min_interval = period / calls
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
    """
    Fetch a URL with automatic retries on failure.
    
    Args:
        url: URL to fetch
        headers: Optional HTTP headers
    
    Returns:
        Response object
    
    Raises:
        requests.RequestException: If all retries fail
    """
    if headers is None:
        headers = {
            'User-Agent': 'WorldCupRosterProject/1.0 (Educational/Research)'
        }
    
    logger.info(f"Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response


def parse_html(html_content: str, parser: str = 'lxml') -> BeautifulSoup:
    """
    Parse HTML content with BeautifulSoup.
    
    Args:
        html_content: HTML string to parse
        parser: Parser to use ('lxml', 'html.parser', etc.)
    
    Returns:
        BeautifulSoup object
    """
    return BeautifulSoup(html_content, parser)


def standardize_position(position: str) -> str:
    """
    Standardize position codes to GK, DF, MF, FW.
    
    Args:
        position: Raw position string
    
    Returns:
        Standardized position code
    """
    position = position.strip().upper()
    
    position_map = {
        'GK': 'GK',
        'GOALKEEPER': 'GK',
        'DF': 'DF',
        'DEF': 'DF',
        'DEFENDER': 'DF',
        'MF': 'MF',
        'MID': 'MF',
        'MIDFIELDER': 'MF',
        'FW': 'FW',
        'FOR': 'FW',
        'FORWARD': 'FW',
        'ATT': 'FW',
        'ATTACKER': 'FW',
        'ST': 'FW',
        'STRIKER': 'FW',
    }
    
    return position_map.get(position, position)


def clean_player_name(name: str) -> str:
    """
    Clean and standardize player names.
    
    Args:
        name: Raw player name
    
    Returns:
        Cleaned player name
    """
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Remove common suffixes
    suffixes = [' (c)', ' (captain)', ' (gk)']
    for suffix in suffixes:
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
    
    return name.strip()


def extract_number_from_text(text: str) -> Optional[int]:
    """
    Extract the first number from a text string.
    
    Args:
        text: Text containing a number
    
    Returns:
        Extracted number or None
    """
    import re
    
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None


def save_to_csv(data: list, filepath: Path, fieldnames: list) -> None:
    """
    Save data to CSV file.
    
    Args:
        data: List of dictionaries
        filepath: Path to save CSV
        fieldnames: List of field names
    """
    import csv
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Saved {len(data)} records to {filepath}")


def load_from_csv(filepath: Path) -> list:
    """
    Load data from CSV file.
    
    Args:
        filepath: Path to CSV file
    
    Returns:
        List of dictionaries
    """
    import csv
    
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    logger.info(f"Loaded {len(data)} records from {filepath}")
    return data


def get_country_code(country_name: str) -> str:
    """
    Get ISO 3166-1 alpha-3 country code from country name.
    
    Args:
        country_name: Country name
    
    Returns:
        Three-letter country code
    """
    # This is a simplified mapping - you may want to use a library like pycountry
    country_codes = {
        'Argentina': 'ARG',
        'Australia': 'AUS',
        'Belgium': 'BEL',
        'Brazil': 'BRA',
        'Cameroon': 'CMR',
        'Canada': 'CAN',
        'Costa Rica': 'CRC',
        'Croatia': 'HRV',
        'Denmark': 'DNK',
        'Ecuador': 'ECU',
        'England': 'ENG',
        'France': 'FRA',
        'Germany': 'GER',
        'Ghana': 'GHA',
        'Iran': 'IRN',
        'Japan': 'JPN',
        'Mexico': 'MEX',
        'Morocco': 'MAR',
        'Netherlands': 'NED',
        'Poland': 'POL',
        'Portugal': 'POR',
        'Qatar': 'QAT',
        'Saudi Arabia': 'KSA',
        'Senegal': 'SEN',
        'Serbia': 'SRB',
        'South Korea': 'KOR',
        'Spain': 'ESP',
        'Switzerland': 'SUI',
        'Tunisia': 'TUN',
        'United States': 'USA',
        'Uruguay': 'URU',
        'Wales': 'WAL',
    }
    
    return country_codes.get(country_name, country_name[:3].upper())

# Made with Bob
