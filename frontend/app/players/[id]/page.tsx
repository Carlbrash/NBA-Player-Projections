"use client";
import {useEffect,useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
type Row={pts:number;reb:number;ast:number;fg3m:number;date_utc:string;home:boolean};
type Stat={projection:number;sd:number;lower80?:number;upper80?:number};
export default function Player({params}:{params:Promise<{id:string}>}){
 const [id,setId]=useState("");const [game,setGame]=useState("");
 const [history,setHistory]=useState<Row[]>([]);
 const [projection,setProjection]=useState<Record<string,Stat>|null>(null);
 const [stat,setStat]=useState("pts"),[line,setLine]=useState("20.5");
 const [over,setOver]=useState<{probability:number;fair_odds:number|null}|null>(null);
 const [error,setError]=useState("");
 useEffect(()=>{params.then(p=>{setId(p.id);fetch(API+"/api/players/"+p.id+"/history").then(r=>r.json()).then(setHistory).catch(e=>setError(String(e)))})},[params]);
 useEffect(()=>{if(!id||!game)return;fetch(API+"/api/players/"+id+"/projection/"+game).then(r=>{if(!r.ok)throw Error("No projection");return r.json()}).then(setProjection).catch(e=>setError(String(e)))},[id,game]);
 async function calculate(){if(!game)return;try{const r=await fetch(API+"/api/players/"+id+"/over?game_id="+game+"&stat="+stat+"&line="+line);if(!r.ok)throw Error("No estimate");setOver(await r.json())}catch(e){setError(String(e))}}
 return <main><h1>Player #{id}</h1>{error&&<p role="alert">{error}</p>}
 <div className="panel"><label>Game ID <input value={game} onChange={e=>setGame(e.target.value)} placeholder="Database game ID"/></label></div>
 {projection&&<div className="panel"><h2>Pregame projections</h2><div className="scroll"><table><thead><tr><th>Stat</th><th>Projection</th><th>80% interval</th></tr></thead><tbody>{Object.entries(projection).map(([k,v])=><tr key={k}><td>{k.toUpperCase()}</td><td>{v.projection.toFixed(1)}</td><td>{(v.lower80??Math.max(0,v.projection-1.2816*v.sd)).toFixed(1)} – {(v.upper80??v.projection+1.2816*v.sd).toFixed(1)}</td></tr>)}</tbody></table></div></div>}
 <div className="panel"><h2>Over / Under</h2><select value={stat} onChange={e=>setStat(e.target.value)}>{["pts","reb","ast","fg3m","pra"].map(s=><option key={s}>{s}</option>)}</select> <input type="number" step=".5" value={line} onChange={e=>setLine(e.target.value)}/> <button onClick={calculate}>Calculate</button>{over&&<p>Over: {(over.probability*100).toFixed(1)}% · Fair odds: {over.fair_odds?.toFixed(2)??"N/A"}</p>}</div>
 <div className="panel scroll"><h2>Last 25 games</h2><table><thead><tr><th>Date</th><th>PTS</th><th>REB</th><th>AST</th><th>3PM</th></tr></thead><tbody>{history.map((r,i)=><tr key={i}><td>{new Date(r.date_utc).toLocaleDateString()}</td><td>{r.pts}</td><td>{r.reb}</td><td>{r.ast}</td><td>{r.fg3m}</td></tr>)}</tbody></table></div></main>
}
