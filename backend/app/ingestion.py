"""Atomic game claims prevent duplicate box-score API requests."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

def claim_game(db: Session, game_id: int, lease_minutes: int = 5) -> bool:
    """Claim an unfinished game. Commit before calling the external API."""
    now = datetime.now(timezone.utc)
    db.execute(text("""
      INSERT INTO ingestion_state(game_id,status)
      VALUES (:game_id,'pending') ON CONFLICT(game_id) DO NOTHING
    """), {"game_id": game_id})
    claimed = db.execute(text("""
      UPDATE ingestion_state SET status='claimed',
        claimed_until=:until, attempts=attempts+1, updated_at=:now
      WHERE game_id=:game_id AND (
        status IN ('pending','failed') OR
        (status='claimed' AND claimed_until < :now))
      RETURNING game_id
    """), {"game_id": game_id, "until": now + timedelta(minutes=lease_minutes), "now": now}).first()
    db.commit()
    return claimed is not None

def complete_game(db: Session, game_id: int) -> None:
    """Call only after box score and players are committed successfully."""
    db.execute(text("""
      UPDATE ingestion_state SET status='complete', completed_at=now(),
        claimed_until=NULL, last_error=NULL, updated_at=now()
      WHERE game_id=:game_id AND status='claimed'
    """), {"game_id": game_id})
    db.commit()

def fail_game(db: Session, game_id: int, error: str) -> None:
    db.execute(text("""
      UPDATE ingestion_state SET status='failed', claimed_until=NULL,
        last_error=:error, updated_at=now()
      WHERE game_id=:game_id AND status='claimed'
    """), {"game_id": game_id, "error": error[:1000]})
    db.commit()
