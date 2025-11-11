import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict

import requests
from dotenv import load_dotenv
from os import getenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
GODADDY_API_URL = "https://api.ote-godaddy.com/v1/domains/available"
BATCH_SIZE = 70
DELAY_SECONDS = 4
DEFAULT_TLD = ".com"
OUTPUT_FILE = "available.json"
DEFAULT_DICTIONARY = "C:\\Users\\USER\\Desktop\\worded_domain_checkr\\words.txt"


class DomainChecker:
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Authorization": f"sso-key {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }
    
    def check_batch(self, domains: List[str]) -> List[Dict]:
        try:
            response = requests.post(
                GODADDY_API_URL,
                headers=self.headers,
                json=domains,
                params={"checkType": "FAST"},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("domains", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []


def load_dictionary_words(dict_path: Path, length: int = None, min_length: int = None, max_length: int = None) -> List[str]:
    try:
        with dict_path.open("r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f if line.strip()]
        
        # Filter by length
        if length is not None:
            words = [w for w in words if len(w) == length]
        else:
            if min_length is not None:
                words = [w for w in words if len(w) >= min_length]
            if max_length is not None:
                words = [w for w in words if len(w) <= max_length]
        
        # Filter to only alphabetic characters
        words = [w for w in words if w.isalpha()]
        
        logger.info(f"Loaded {len(words):,} words from dictionary")
        return words
        
    except FileNotFoundError:
        logger.error(f"Dictionary file not found: {dict_path}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Error reading dictionary file: {e}")
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check domain availability for dictionary words using GoDaddy API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python domain_checker.py --length 3 --tlds .com,.io
  python domain_checker.py --min-length 3 --max-length 5 --tlds .com
  python domain_checker.py --dict custom_words.txt --length 4"""
    )
    
    length_group = parser.add_mutually_exclusive_group()
    length_group.add_argument(
        "--length",
        type=int,
        help="Exact number of letters in domain words"
    )
    length_group.add_argument(
        "--min-length",
        type=int,
        help="Minimum number of letters in domain words"
    )
    
    parser.add_argument(
        "--max-length",
        type=int,
        help="Maximum number of letters in domain words (use with --min-length)"
    )
    parser.add_argument(
        "--tlds",
        default=DEFAULT_TLD,
        help=f"Comma-separated TLDs (default: {DEFAULT_TLD})"
    )
    parser.add_argument(
        "--dict",
        type=Path,
        default=Path(DEFAULT_DICTIONARY),
        help=f"Path to dictionary file (default: {DEFAULT_DICTIONARY})"
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.length is not None and args.length < 1:
        parser.error("Length must be at least 1")
    
    if args.min_length is not None and args.min_length < 1:
        parser.error("Minimum length must be at least 1")
    
    if args.max_length is not None and args.min_length is None:
        parser.error("--max-length requires --min-length")
    
    if args.min_length is not None and args.max_length is not None:
        if args.max_length < args.min_length:
            parser.error("Maximum length must be greater than or equal to minimum length")
    
    if args.length is None and args.min_length is None:
        parser.error("Either --length or --min-length must be specified")
    
    return args


def load_credentials() -> tuple[str, str]:
    load_dotenv()
    
    api_key = getenv("GODADDY_API_KEY")
    api_secret = getenv("GODADDY_API_SECRET")
    
    if not api_key or not api_secret:
        logger.error("Missing GoDaddy API credentials in .env file")
        sys.exit(1)
    
    return api_key, api_secret


def save_results(results: Dict[str, List[str]], output_path: Path) -> None:
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_path}")
    except IOError as e:
        logger.error(f"Failed to save results: {e}")


def main() -> None:
    args = parse_arguments()
    api_key, api_secret = load_credentials()
    
    # Parse TLDs
    tlds = [tld.strip() for tld in args.tlds.split(",") if tld.strip()]
    
    # Load dictionary words
    logger.info(f"Loading dictionary words from {args.dict}")
    words = load_dictionary_words(
        args.dict,
        length=args.length,
        min_length=args.min_length,
        max_length=args.max_length
    )
    
    if not words:
        logger.error("No words found matching the criteria")
        sys.exit(1)
    
    # Initialize checker
    checker = DomainChecker(api_key, api_secret)
    
    # Check domains for each TLD
    available_domains = {tld: [] for tld in tlds}
    
    for tld in tlds:
        logger.info(f"Checking {tld} domains...")
        
        for i in range(0, len(words), BATCH_SIZE):
            batch = [f"{word}{tld}" for word in words[i:i + BATCH_SIZE]]
            results = checker.check_batch(batch)
            
            for result in results:
                domain = result.get("domain")
                if result.get("available"):
                    available_domains[tld].append(domain)
                    logger.info(f"✓ Available: {domain}")
                else:
                    logger.debug(f"✗ Taken: {domain}")
            
            processed = min(i + BATCH_SIZE, len(words))
            logger.info(f"Progress: {processed}/{len(words)} for {tld}")
            
            # Rate limiting
            if i + BATCH_SIZE < len(words):
                time.sleep(DELAY_SECONDS)
    
    # Save results
    save_results(available_domains, Path(OUTPUT_FILE))
    
    # Summary
    total_available = sum(len(domains) for domains in available_domains.values())
    logger.info(f"Complete! Found {total_available} available domains")


if __name__ == "__main__":
    main()