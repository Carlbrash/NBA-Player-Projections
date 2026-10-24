"use client";
import {useEffect,useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
type Status={utc_date:string;calls_used:number;remaining:number};
export default function SettingsClient(){
 const [status,setStatus]=useState<Status|null>(null),[error,setError]=useState("");
 useEffect(()=>{fetch(API+"/api/status").then(r=>{if(!r.ok)throw Error("Status unavailable");return r.json()}).then(setStatus).catch(e=>setError(String(e)))},[]);
 return <main><h1>Settings & API usage</h1><div className="panel"><h2>Daily API budget</h2>{status?<p>{status.calls_used} / 90 calls · {status.remaining} remaining · {status.utc_date} UTC</p>:<p>{error||"Loading..."}</p>}<p className="muted">Scheduled updates and manual update controls require backend deployment and protected admin access.</p></div></main>
}
