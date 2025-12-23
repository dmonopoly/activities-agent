"""Background scheduler for periodic web scraping."""
import threading
from typing import Optional
from datetime import datetime

from services.scraper_job import run_scrape_job, SCRAPE_INTERVAL_SECONDS

# Global state for the scheduler
_scheduler_thread: Optional[threading.Thread] = None
_scheduler_stop_event: Optional[threading.Event] = None
_is_running = False


def _scraper_loop(stop_event: threading.Event, interval: int):
    """
    Internal loop that runs the scraper periodically.
    
    Args:
        stop_event: Event to signal the loop to stop
        interval: Seconds between scrape runs
    """
    print(f"[SCHEDULER] Scraper loop started, interval={interval}s")
    
    try:
        run_scrape_job()
    except Exception as e:
        print(f"[SCHEDULER] Initial scrape failed: {e}")
    
    while not stop_event.is_set():
        # Wait for the interval, but check stop_event periodically
        if stop_event.wait(timeout=interval):
            # stop_event was set, exit the loop
            break
        
        # Run the scrape job
        try:
            print(f"[SCHEDULER] Running scheduled scrape at {datetime.utcnow().isoformat()}")
            run_scrape_job()
        except Exception as e:
            print(f"[SCHEDULER] Scheduled scrape failed: {e}")
    
    print("[SCHEDULER] Scraper loop stopped")


def start_scraper_scheduler(interval: Optional[int] = None) -> bool:
    """
    Start the background scraper scheduler.
    
    Args:
        interval: Optional override for scrape interval in seconds.
                  Defaults to SCRAPE_INTERVAL_SECONDS (env: SCRAPE_INTERVAL_SECONDS)
    
    Returns:
        True if scheduler started, False if already running
    """
    global _scheduler_thread, _scheduler_stop_event, _is_running
    
    if _is_running:
        print("[SCHEDULER] Scheduler already running")
        return False
    
    scrape_interval = interval if interval is not None else SCRAPE_INTERVAL_SECONDS
    
    _scheduler_stop_event = threading.Event()
    _scheduler_thread = threading.Thread(
        target=_scraper_loop,
        args=(_scheduler_stop_event, scrape_interval),
        daemon=True,  # Thread will be killed when main process exits
        name="ScraperScheduler"
    )
    _scheduler_thread.start()
    _is_running = True
    
    print(f"[SCHEDULER] Started scraper scheduler (interval: {scrape_interval}s)")
    return True


def stop_scraper_scheduler(timeout: float = 5.0) -> bool:
    """
    Stop the background scraper scheduler.
    
    Args:
        timeout: Maximum seconds to wait for graceful shutdown
    
    Returns:
        True if scheduler stopped, False if wasn't running
    """
    global _scheduler_thread, _scheduler_stop_event, _is_running
    
    if not _is_running or _scheduler_stop_event is None:
        print("[SCHEDULER] Scheduler not running")
        return False
    
    print("[SCHEDULER] Stopping scraper scheduler...")
    _scheduler_stop_event.set()
    
    if _scheduler_thread is not None:
        _scheduler_thread.join(timeout=timeout)
        if _scheduler_thread.is_alive():
            print("[SCHEDULER] Warning: Scheduler thread did not stop gracefully")
    
    _scheduler_thread = None
    _scheduler_stop_event = None
    _is_running = False
    
    print("[SCHEDULER] Scraper scheduler stopped")
    return True


def is_scheduler_running() -> bool:
    """Check if the scheduler is currently running."""
    return _is_running


def get_scheduler_status() -> dict:
    """
    Get the current status of the scraper scheduler.
    
    Returns:
        Dict with scheduler status info
    """
    return {
        "running": _is_running,
        "interval_seconds": SCRAPE_INTERVAL_SECONDS,
        "thread_name": _scheduler_thread.name if _scheduler_thread else None,
        "thread_alive": _scheduler_thread.is_alive() if _scheduler_thread else False
    }

