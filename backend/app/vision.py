"""Server-side OpenAI vision extraction for NBA box score images."""
import base64
import json
import os
import httpx

SYSTEM_PROMPT="""Extract NBA box score data from the supplied image.
Return ONLY valid JSON with teams (array), warnings (array).
Each team: name, totals {pts,reb,ast}, players (array).
Each participating player: name,min,pts,fgm,fga,fg3m,fg3a,ftm,fta,
reb,ast,tov,stl,blk,plus_minus. Skip DNP rows.
Never guess obscured or unreadable values: use null and add warnings.
All numeric stats must be JSON numbers, not strings. Minutes are MM:SS.
Do not invent teams or players not shown in the image."""

class VisionError(RuntimeError): pass

async def extract_boxscore(image:bytes,mime_type:str)->dict:
    key=os.environ.get("OPENAI_API_KEY")
    if not key: raise VisionError("OPENAI_API_KEY is not configured")
    model=os.environ.get("VISION_MODEL","gpt-4.1")
    payload={
      "model":model,
      "temperature":0,
      "response_format":{"type":"json_object"},
      "messages":[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":[
          {"type":"text","text":"Extract all visible NBA box-score players and team totals."},
          {"type":"image_url","image_url":{"url":"data:"+mime_type+";base64,"+
            base64.b64encode(image).decode("ascii")}}
        ]}
      ]
    }
    async with httpx.AsyncClient(timeout=90) as client:
        response=await client.post("https://api.openai.com/v1/chat/completions",
          headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
          json=payload)
    response.raise_for_status()
    result=response.json()
    try:
        data=json.loads(result["choices"][0]["message"]["content"])
    except (KeyError,IndexError,TypeError,ValueError) as exc:
        raise VisionError("Vision returned invalid JSON") from exc
    if not isinstance(data.get("teams"),list):
        raise VisionError("Vision response missing teams")
    return data
