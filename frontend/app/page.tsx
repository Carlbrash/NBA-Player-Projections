"use client";
import {useEffect,useState} from "react";
type Game={id:number;date_utc:string;home_team:string;away_team:string;status:string};
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export default function Home(){
 const [date,setDate]=useState(new Date().toISOString().slice(0,10));
 const [games,setGames]=useState<Game[]>([]);
 const [error,setError]=useState("");
 useEffect(()=>{fetch(API+"/api/games?day="+date).then(r=>{if(!r.ok)throw Error("API error");return r.json()}).then(setGames).catch(e=>setError(e.message))},[date]);
 return <main><h1>Today&apos;s NBA games</h1><p className="muted">Pregame analysis only · No live data</p>
 <div className="panel"><label>UTC date <input type="date" value={date} onChange={e=>setDate(e.target.value)}/></label></div>
 {error&&<p role="alert">{error}</p>}
 <div className="panel scroll"><table><thead><tr><th>Tipoff (UTC)</th><th>Matchup</th><th>Status</th><th>Players</th></tr></thead>
 <tbody>{games.map(g=><tr key={g.id}><td>{new Date(g.date_utc).toLocaleString()}</td><td>{g.away_team} @ {g.home_team}</td><td>{g.status}</td><td>Pending projection pipeline</td></tr>)}</tbody></table>
 {!games.length&&<p className="muted">No cached games for this date. This page never calls the external NBA API.</p>}</div></main>
}
