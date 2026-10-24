"use client";
import {useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export default function UploadClient(){
 const [token,setToken]=useState(""),[game,setGame]=useState(""),[file,setFile]=useState<File|null>(null);
 const [preview,setPreview]=useState("[]"),[previewId,setPreviewId]=useState(""),[result,setResult]=useState("");
 async function upload(){
  if(!file||!game)return;const form=new FormData();form.append("file",file);form.append("game_id",game);
  const r=await fetch(API+"/api/screenshots/preview",{method:"POST",headers:{"x-admin-token":token},body:form});
  const data=await r.json();if(!r.ok){setResult(JSON.stringify(data));return}
  setPreviewId(data.preview_id);setPreview(JSON.stringify(data.rows,null,2));setResult(data.message||"Review before saving");
 }
 async function confirm(){
  try{const rows=JSON.parse(preview);const r=await fetch(API+"/api/screenshots/confirm",{
   method:"POST",headers:{"Content-Type":"application/json","x-admin-token":token},
   body:JSON.stringify({preview_id:previewId,game_id:Number(game),rows})});
   const data=await r.json();setResult(JSON.stringify(data));
  }catch(e){setResult(String(e))}
 }
 return <main><h1>Box-score screenshot review</h1><p className="muted">PNG/JPG · Manual confirmation required</p>
 <div className="panel"><input type="password" placeholder="Admin token" value={token} onChange={e=>setToken(e.target.value)}/> <input type="number" placeholder="Game ID" value={game} onChange={e=>setGame(e.target.value)}/> <input type="file" accept="image/png,image/jpeg" onChange={e=>setFile(e.target.files?.[0]||null)}/> <button onClick={upload}>Upload</button></div>
 {previewId&&<div className="panel"><h2>Review extracted rows</h2><p>JSON rows can be edited before confirmation. Player IDs must be matched first.</p><textarea style={{width:"100%",minHeight:250,background:"#26334b",color:"white"}} value={preview} onChange={e=>setPreview(e.target.value)}/><p><button onClick={confirm}>Confirm and save</button></p></div>}
 {result&&<div className="panel" role="status">{result}</div>}</main>
}
