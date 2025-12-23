"""
Site-specific scrapers for NYC events.

Each scraper returns a list of activity dictionaries with the following fields:

Activity Dict Fields:
    name (str): Event/activity name (max 200 chars)
    location (str): Venue or neighborhood (max 100 chars), defaults to "NYC"
    description (str): Event description/summary (max 500 chars)
    price (str): Price info, e.g. "Free", "$25", "Free/Cheap"
    date (str): Date/time string as scraped, e.g. "Dec 24, 7pm", "Saturday"
    url (str): Direct link to the event page
    source (str): Source site identifier: "theskint", "timeout", or "eventbrite"
    category (str): Auto-categorized category, one of:
        Music, Comedy, Arts, Theater, Food & Drink, Fitness, Outdoor,
        Nightlife, Workshop, Networking, Film, Sports, Family, Festival, Other
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

# Common headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REQUEST_TIMEOUT = 15  # seconds

# Category keywords for auto-categorization
CATEGORY_KEYWORDS = {
    "Music": ["concert", "music", "band", "dj", "jazz", "rock", "hip hop", "classical", "orchestra", "live music"],
    "Comedy": ["comedy", "standup", "stand-up", "comedian", "improv", "laugh"],
    "Arts": ["art", "gallery", "museum", "exhibition", "painting", "sculpture", "photography"],
    "Theater": ["theater", "theatre", "play", "musical", "broadway", "off-broadway", "drama"],
    "Food & Drink": ["food", "drink", "tasting", "wine", "beer", "cocktail", "restaurant", "dining", "brunch", "dinner"],
    "Fitness": ["yoga", "fitness", "workout", "run", "running", "cycling", "gym", "exercise", "dance class"],
    "Outdoor": ["outdoor", "park", "hiking", "nature", "garden", "rooftop", "picnic", "walking tour"],
    "Nightlife": ["party", "club", "nightclub", "nightlife", "dancing", "bar crawl"],
    "Workshop": ["workshop", "class", "learn", "course", "tutorial", "seminar"],
    "Networking": ["networking", "meetup", "social", "mixer", "professional"],
    "Film": ["film", "movie", "cinema", "screening", "documentary"],
    "Sports": ["sports", "game", "match", "basketball", "baseball", "football", "soccer"],
    "Family": ["family", "kids", "children", "kid-friendly"],
    "Festival": ["festival", "fair", "market", "street fair"],
}


def _categorize_event(text: str) -> str:
    """
    Categorize an event based on keywords in its text.
    
    Args:
        text: Combined name and description text
        
    Returns:
        Category string (see module docstring for valid values)
    """
    text_lower = text.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return category
    
    return "Other"


def _make_activity(
    name: str,
    location: str,
    description: str,
    price: str,
    date: str,
    url: str,
    source: str
) -> Dict[str, Any]:
    """
    Create a normalized activity dictionary with auto-categorization.
    
    Returns:
        Activity dict with all required fields (see module docstring)
    """
    return {
        "name": name[:200] if name else "",
        "location": location[:100] if location else "NYC",
        "description": description[:500] if description else "",
        "price": price if price else "",
        "date": date[:100] if date else "",
        "url": url if url else "",
        "source": source,
        "category": _categorize_event(f"{name} {description}")
    }


def scrape_theskint() -> List[Dict[str, Any]]:
    """
    Scrape free and cheap events from theskint.com.
    
    The Skint is a daily email newsletter listing free and cheap events in NYC.
    
    Returns:
        List of activity dicts (see module docstring for field definitions)
    """
    activities = []
    url = "https://www.theskint.com/"
    
    print(f"[SCRAPER] Fetching theskint.com...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[SCRAPER] Error fetching theskint.com: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try finding event entries - The Skint uses various div structures
    event_containers = soup.find_all("div", class_=re.compile(r"entry|post|event", re.I))
    
    if not event_containers:
        event_containers = soup.find_all("article")
    
    if not event_containers:
        event_containers = soup.find_all("li")
    
    for container in event_containers[:30]:
        try:
            title_elem = container.find(["h2", "h3", "h4", "a"])
            if not title_elem:
                continue
            
            name = title_elem.get_text(strip=True)
            if not name or len(name) < 5:
                continue
            
            link = container.find("a", href=True)
            event_url = link["href"] if link else url
            if event_url and not event_url.startswith("http"):
                event_url = "https://www.theskint.com" + event_url
            
            desc_elem = container.find("p")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            full_text = container.get_text()
            date_match = re.search(
                r'(today|tonight|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}/\d{1,2}|\w+ \d{1,2})',
                full_text, re.I
            )
            event_date = date_match.group(0) if date_match else ""
            
            price_match = re.search(r'\$\d+|\bfree\b', full_text, re.I)
            price = price_match.group(0) if price_match else "Free/Cheap"
            
            activities.append(_make_activity(
                name=name,
                location="NYC",
                description=description,
                price=price,
                date=event_date,
                url=event_url,
                source="theskint"
            ))
            
        except Exception as e:
            print(f"[SCRAPER] Error parsing theskint event: {e}")
            continue
    
    print(f"[SCRAPER] Found {len(activities)} events from theskint.com")
    return activities


def scrape_timeout() -> List[Dict[str, Any]]:
    """
    Scrape events from timeout.com/newyork.
    
    Time Out NYC has curated event listings and things to do.
    
    Returns:
        List of activity dicts (see module docstring for field definitions)
    """
    activities = []
    url = "https://www.timeout.com/newyork/things-to-do"
    
    print(f"[SCRAPER] Fetching timeout.com/newyork...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[SCRAPER] Error fetching timeout.com: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    cards = soup.find_all("article")
    if not cards:
        cards = soup.find_all("div", class_=re.compile(r"card|listing|tile", re.I))
    
    for card in cards[:30]:
        try:
            title_elem = card.find(["h2", "h3", "h4"])
            if not title_elem:
                title_elem = card.find("a")
            
            if not title_elem:
                continue
            
            name = title_elem.get_text(strip=True)
            if not name or len(name) < 5:
                continue
            
            link = card.find("a", href=True)
            event_url = link["href"] if link else url
            if event_url and not event_url.startswith("http"):
                event_url = "https://www.timeout.com" + event_url
            
            desc_elem = card.find("p")
            if not desc_elem:
                desc_elem = card.find("div", class_=re.compile(r"summary|description|excerpt", re.I))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            location_elem = card.find(class_=re.compile(r"location|venue|neighborhood", re.I))
            location = location_elem.get_text(strip=True) if location_elem else "NYC"
            
            price_elem = card.find(class_=re.compile(r"price|cost", re.I))
            full_text = card.get_text()
            if price_elem:
                price = price_elem.get_text(strip=True)
            else:
                price_match = re.search(r'\$\d+|\bfree\b', full_text, re.I)
                price = price_match.group(0) if price_match else ""
            
            date_elem = card.find(class_=re.compile(r"date|time|when", re.I))
            event_date = date_elem.get_text(strip=True) if date_elem else ""
            
            activities.append(_make_activity(
                name=name,
                location=location,
                description=description,
                price=price,
                date=event_date,
                url=event_url,
                source="timeout"
            ))
            
        except Exception as e:
            print(f"[SCRAPER] Error parsing timeout event: {e}")
            continue
    
    print(f"[SCRAPER] Found {len(activities)} events from timeout.com")
    return activities


def scrape_eventbrite() -> List[Dict[str, Any]]:
    """
    Scrape events from eventbrite.com for NYC.
    
    Eventbrite is a popular event ticketing platform.
    
    Returns:
        List of activity dicts (see module docstring for field definitions)
    """
    activities = []
    url = "https://www.eventbrite.com/d/ny--new-york/events/"
    
    print(f"[SCRAPER] Fetching eventbrite.com NYC events...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[SCRAPER] Error fetching eventbrite.com: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    cards = soup.find_all("div", class_=re.compile(r"event-card|search-event", re.I))
    if not cards:
        cards = soup.find_all("article")
    if not cards:
        cards = soup.find_all("a", href=re.compile(r"eventbrite\.com/e/", re.I))
    
    seen_urls = set()
    
    for card in cards[:30]:
        try:
            if card.name == "a":
                link = card
                name = card.get_text(strip=True)
                container = card.parent
            else:
                link = card.find("a", href=True)
                title_elem = card.find(["h2", "h3", "h4"])
                name = title_elem.get_text(strip=True) if title_elem else ""
                container = card
            
            if not link or not link.get("href"):
                continue
            
            event_url = link["href"]
            if not event_url.startswith("http"):
                event_url = "https://www.eventbrite.com" + event_url
            
            if event_url in seen_urls:
                continue
            seen_urls.add(event_url)
            
            if not name:
                name = link.get_text(strip=True)
            
            if not name or len(name) < 5:
                continue
            
            desc_elem = container.find("p") if container else None
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            location_elem = container.find(class_=re.compile(r"location|venue", re.I)) if container else None
            location = location_elem.get_text(strip=True) if location_elem else "New York, NY"
            
            date_elem = container.find(class_=re.compile(r"date|time", re.I)) if container else None
            full_text = container.get_text() if container else ""
            if date_elem:
                event_date = date_elem.get_text(strip=True)
            else:
                date_match = re.search(
                    r'(\w{3,9}\s+\d{1,2}(?:,?\s+\d{4})?)|(\d{1,2}/\d{1,2})',
                    full_text
                )
                event_date = date_match.group(0) if date_match else ""
            
            price_elem = container.find(class_=re.compile(r"price|ticket", re.I)) if container else None
            if price_elem:
                price = price_elem.get_text(strip=True)
            else:
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?|\bfree\b', full_text, re.I)
                price = price_match.group(0) if price_match else ""
            
            activities.append(_make_activity(
                name=name,
                location=location,
                description=description,
                price=price,
                date=event_date,
                url=event_url,
                source="eventbrite"
            ))
            
        except Exception as e:
            print(f"[SCRAPER] Error parsing eventbrite event: {e}")
            continue
    
    print(f"[SCRAPER] Found {len(activities)} events from eventbrite.com")
    return activities


def scrape_all_sites() -> List[Dict[str, Any]]:
    """
    Scrape all configured sites and combine results.
    
    Returns:
        Combined list of activity dicts from all sources, deduplicated by URL
        (see module docstring for field definitions)
    """
    all_activities = []
    
    scrapers = [
        ("theskint", scrape_theskint),
        ("timeout", scrape_timeout),
        ("eventbrite", scrape_eventbrite),
    ]
    
    for name, scraper_func in scrapers:
        try:
            activities = scraper_func()
            all_activities.extend(activities)
        except Exception as e:
            print(f"[SCRAPER] Error running {name} scraper: {e}")
            continue
    
    # Deduplicate by URL
    seen_urls = set()
    unique_activities = []
    for activity in all_activities:
        url = activity.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_activities.append(activity)
        elif not url:
            unique_activities.append(activity)
    
    print(f"[SCRAPER] Total unique activities scraped: {len(unique_activities)}")
    return unique_activities

