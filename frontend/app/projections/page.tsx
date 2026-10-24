"use client";
import {useEffect,useMemo,useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
type P={player_id:number;game_id:number;player_name:string;team_name:string;date_utc:string;proj_pts:number;proj_reb:number;proj_ast:number;proj_fg3m:number;proj_pra:number;sd_pts:number};
export default function Projections(){
 const [date,setDate]=useState(new Date().toISOString().slice(0,10)),[search,setSearch]=useState(""),[team,setTeam]=useState(""),[sort,setSort]=useState<keyof P>("proj_pts"),[data,setData]=useState<P[]>([]),[error,setError]=useState("");
 useEffect(()=>{fetch(API+"/api/projections?day="+date).then(r=>{if(!r.ok)throw Error("API unavailable");return r.json()}).then(setData).catch(e=>setError(String(e)))},[date]);
 const teams=Array.from(new Set(data.map(r=>r.team_name))).sort();
 const rows=useMemo(()=>data.filter(r=>(!team||r.team_name===team)&&r.player_name.toLowerCase().includes(search.toLowerCase())).sort((a,b)=>Number(b[sort]??0)-Number(a[sort]??0)),[data,team,search,sort]);
 return <main><h1>Pregame player projections</h1><p className="muted">Saved pregame snapshots · No live betting</p>
 <div className="panel"><input type="date" value={date} onChange={e=>setDate(e.target.value)}/> <input placeholder="Search player" value={search} onChange={e=>setSearch(e.target.value)}/> <select value={team} onChange={e=>setTeam(e.target.value)}><option value="">All teams</option>{teams.map(t=><option key={t}>{t}</option>)}</select> <select value={sort} onChange={e=>setSort(e.target.value as keyof P)}>{["proj_pts","proj_reb","proj_ast","proj_fg3m","proj_pra"].map(k=><option key={k} value={k}>{k.replace("proj_","").toUpperCase()}</option>)}</select></div>
 {error&&<p role="alert">{error}</p>}<div className="panel scroll"><table><thead><tr><th>Player</th><th>Team</th><th>PTS (80%)</th><th>REB</th><th>AST</th><th>3PM</th><th>PRA</th></tr></thead><tbody>{rows.map(r=><tr key={r.player_id+"-"+r.game_id}><td><a href={"/players/"+r.player_id}>{r.player_name}</a></td><td>{r.team_name}</td><td>{r.proj_pts.toFixed(1)} ({Math.max(0,r.proj_pts-1.2816*r.sd_pts).toFixed(1)}–{(r.proj_pts+1.2816*r.sd_pts).toFixed(1)})</td><td>{r.proj_reb.toFixed(1)}</td><td>{r.proj_ast.toFixed(1)}</td><td>{r.proj_fg3m.toFixed(1)}</td><td>{r.proj_pra.toFixed(1)}</td></tr>)}</tbody></table>{!rows.length&&<p>No saved projections for this date.</p>}</div></main>
}
