from datetime import datetime,timezone
from app.scheduler import utc_schedule_dates

def test_utc_dates_cover_dst_boundary():
    before=utc_schedule_dates(datetime(2026,10,24,6,tzinfo=timezone.utc))
    after=utc_schedule_dates(datetime(2026,10,26,6,tzinfo=timezone.utc))
    assert len(before)>=3
    assert len(after)>=3
    assert all(len(s)==10 for s in before+after)
