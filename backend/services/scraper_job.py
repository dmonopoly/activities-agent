"""
Scraper job orchestration.

This module provides the run_scrape_job function that orchestrates
scraping all sites and updating the cache.
"""
import os
from datetime import datetime
from typing import Dict, Any

from services.scraper_sites import scrape_all_sites
from services.scraper_cache import save_cache

# Scrape interval in seconds (default: 10 minutes)
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", "600"))


def run_scrape_job() -> Dict[str, Any]:
    """
    Run a full scrape job across all configured sites.
    
    This function:
    1. Scrapes all configured sites (theskint, timeout, eventbrite)
    2. Saves results to the cache
    3. Returns statistics about the scrape
    
    Returns:
        Dict with:
            - success (bool): Whether save succeeded
            - total_activities (int): Number of activities scraped
            - by_source (dict): Count breakdown by source
            - duration_seconds (float): Scrape duration
            - timestamp (str): ISO timestamp
    """
    start_time = datetime.utcnow()
    print(f"[SCRAPER] Starting scrape job at {start_time.isoformat()}")
    
    activities = scrape_all_sites()
    save_success = save_cache(activities)
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    sources = {}
    for a in activities:
        source = a.get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    result = {
        "success": save_success,
        "total_activities": len(activities),
        "by_source": sources,
        "duration_seconds": round(duration, 2),
        "timestamp": end_time.isoformat() + "Z"
    }
    
    print(f"[SCRAPER] Scrape job completed: {result}")
    return result

