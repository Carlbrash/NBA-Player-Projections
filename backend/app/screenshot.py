"""Manual-confirmation screenshot ingestion. No automatic persistence on extraction."""
import json
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import text
from .config import Settings
from .database import session_factory
from .persist import normalized_name

router=APIRouter(prefix="/api/screenshots",tags=["screenshots"])
TEMP=Path("/tmp/nba-screenshot-previews")
MAX_BYTES=8*1024*1024

def authorized(token:str|None):
    expected=os.environ.get("ADMIN_TOKEN")
    if not expected or token!=expected:
        raise HTTPException(401,"Admin token required")

def validate_rows(rows:list[dict])->list[str]:
    errors=[]
    for i,r in enumerate(rows):
        if r.get("dnp"):continue
        try:
            pts=int(r["pts"]);fgm=int(r["fgm"]);fg3m=int(r["fg3m"]);ftm=int(r["ftm"])
            if pts!=2*fgm+fg3m+ftm:errors.append(f"row {i}: points mismatch")
            for key in ("reb","ast","fga","fta","tov","stl","blk"):
                if int(r[key])<0:errors.append(f"row {i}: negative {key}")
        except (KeyError,ValueError,TypeError):
            errors.append(f"row {i}: missing or invalid statistics")
    return errors

@router.post("/preview")
async def preview(file:UploadFile=File(...),game_id:int=Form(...),x_admin_token:str|None=Header(None)):
    authorized(x_admin_token)
    if file.content_type not in ("image/png","image/jpeg"):
        raise HTTPException(400,"PNG or JPG only")
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise HTTPException(413,"Image too large")
    # Extraction provider is intentionally not fabricated. Return an editable
    # preview object for manually entering or pasting reviewed JSON rows.
    token=str(uuid.uuid4())
    TEMP.mkdir(parents=True,exist_ok=True)
    (TEMP/(token+".json")).write_text(json.dumps({"game_id":game_id,"rows":[]}))
    return {"preview_id":token,"game_id":game_id,"rows":[],
            "message":"Image accepted. Vision provider not configured; enter extracted rows for review."}

class Confirmation(BaseModel):
    preview_id:str
    game_id:int
    rows:list[dict]

@router.post("/confirm")
def confirm(payload:Confirmation,x_admin_token:str|None=Header(None)):
    authorized(x_admin_token)
    if not (TEMP/(payload.preview_id+".json")).exists():
        raise HTTPException(404,"Preview expired")
    errors=validate_rows(payload.rows)
    if errors:raise HTTPException(422,{"mismatches":errors})
    if not payload.rows:raise HTTPException(422,"No player rows")
    with session_factory(Settings())() as db:
        game=db.execute(text("""
          SELECT home_team_id,away_team_id FROM games WHERE id=:id
        """),{"id":payload.game_id}).mappings().first()
        if game is None:raise HTTPException(404,"Game not found")
        try:
            saved=0
            for r in payload.rows:
                if r.get("dnp"):continue
                team_id=int(r["team_id"])
                if team_id not in (game["home_team_id"],game["away_team_id"]):
                    raise HTTPException(422,"Invalid team")
                opponent=game["away_team_id"] if team_id==game["home_team_id"] else game["home_team_id"]
                player_id=r.get("player_id")
                if not player_id:raise HTTPException(422,"Match or create players before saving")
                existing=db.execute(text("""
                  SELECT source FROM player_games WHERE player_id=:p AND game_id=:g
                """),{"p":player_id,"g":payload.game_id}).scalar_one_or_none()
                if existing=="api":continue
                db.execute(text("""
                  INSERT INTO player_games(player_id,game_id,team_id,opp_team_id,home,
                    min,pts,reb,ast,fg3m,fgm,fga,ftm,fta,stl,blk,tov,plus_minus,source)
                  VALUES (:player_id,:game_id,:team_id,:opponent,:home,:min,:pts,:reb,
                    :ast,:fg3m,:fgm,:fga,:ftm,:fta,:stl,:blk,:tov,:plus_minus,'screenshot')
                  ON CONFLICT(player_id,game_id) DO UPDATE SET
                    min=EXCLUDED.min,pts=EXCLUDED.pts,reb=EXCLUDED.reb,
                    ast=EXCLUDED.ast,fg3m=EXCLUDED.fg3m,fgm=EXCLUDED.fgm,
                    fga=EXCLUDED.fga,ftm=EXCLUDED.ftm,fta=EXCLUDED.fta,
                    stl=EXCLUDED.stl,blk=EXCLUDED.blk,tov=EXCLUDED.tov,
                    plus_minus=EXCLUDED.plus_minus,source='screenshot'
                  WHERE player_games.source='screenshot'
                """),{**r,"game_id":payload.game_id,"team_id":team_id,
                       "opponent":opponent,"home":team_id==game["home_team_id"]})
                saved+=1
            db.commit()
        except Exception:
            db.rollback()
            raise
    (TEMP/(payload.preview_id+".json")).unlink(missing_ok=True)
    return {"saved":saved,"source":"screenshot"}
