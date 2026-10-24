from datetime import datetime,timezone
from app.scheduler import utc_schedule_dates

def test_athens_dst_dates_are_unique():
    dates=utc_schedule_dates(datetime(2026,10,25,7,tzinfo=timezone.utc))
    assert dates==sorted(set(dates))
    assert "2026-10-25" in dates
