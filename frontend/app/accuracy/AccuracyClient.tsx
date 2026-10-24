"use client";
import {useEffect,useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
type Row={week:string;stat:string;n:number;model_mae:number;baseline_mae:number};
export default function AccuracyClient(){const [rows,setRows]=useState<Row[]>([]),[error,setError]=useState("");useEffect(()=>{fetch(API+"/api/accuracy").then(r=>{if(!r.ok)throw Error("API unavailable");return r.json()}).then(setRows).catch(e=>setError(String(e)))},[]);return <main><h1>Weekly accuracy</h1><p>MAE: saved pregame projection versus historical average</p>{error&&<p>{error}</p>}<div className="panel scroll"><table><thead><tr><th>Week</th><th>Stat</th><th>Games</th><th>Model MAE</th><th>Baseline MAE</th></tr></thead><tbody>{rows.map((r,i)=><tr key={i}><td>{r.week}</td><td>{r.stat.toUpperCase()}</td><td>{r.n}</td><td>{r.model_mae.toFixed(2)}</td><td>{r.baseline_mae.toFixed(2)}</td></tr>)}</tbody></table></div></main>}
