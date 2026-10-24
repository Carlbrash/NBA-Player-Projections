import "./PlayerStatRow.css";

export type PlayerStatRowData = {
  playerId:number; gameId:number; name:string; jerseyNumber:number|null;
  teamCode:string; matchup:string; photoUrl:string|null; teamLogoUrl:string|null;
  pts:number|null; reb:number|null; ast:number|null; fg3m:number|null; pra:number|null;
  sdPts?:number|null;sdReb?:number|null;sdAst?:number|null;sdFg3m?:number|null;sdPra?:number|null;
  formLast5?:number|null;formChangePct?:number|null;
};
type Props={data:PlayerStatRowData;mode:"pregame"|"final"};
const format=(value:number|null|undefined)=>value==null?"—":value.toFixed(1);
function Metric({value,sd,mode}:{value:number|null;sd?:number|null;mode:"pregame"|"final"}){
  return <span className="psr-metric"><strong>{mode==="final"?(value==null?"—":String(value)):format(value)}</strong>
  {mode==="pregame"&&value!=null&&sd!=null&&<small>{Math.max(0,value-1.2816*sd).toFixed(1)}–{(value+1.2816*sd).toFixed(1)}</small>}</span>;
}
export default function PlayerStatRow({data,mode}:Props){
  const metrics:[number|null,number|null|undefined][]=[
    [data.pts,data.sdPts],[data.reb,data.sdReb],[data.ast,data.sdAst],
    [data.fg3m,data.sdFg3m],[data.pra,data.sdPra]
  ];
  return <div className="psr-row" role="row" data-mode={mode}>
    <div className="psr-player" role="cell">
      <span className="psr-jersey">{data.jerseyNumber??"—"}</span>
      <div className="psr-portrait">{data.photoUrl?<img src={data.photoUrl} alt={data.name} loading="lazy"/>:<span className="psr-fallback">NBA</span>}</div>
      <div className="psr-identity">
        <div className="psr-name-line"><a href={`/players/${data.playerId}`}>{data.name}</a>
          {data.teamLogoUrl&&<img className="psr-team-logo" src={data.teamLogoUrl} alt={data.teamCode} loading="lazy"/>}</div>
        <div className="psr-subline"><b>{data.teamCode}</b><span className="psr-separator">|</span><span>{data.matchup}</span></div>
      </div>
    </div>
    {metrics.map(([value,sd],i)=><div className="psr-stat" role="cell" key={i}><Metric value={value} sd={sd} mode={mode}/></div>)}
    <div className="psr-form" role="cell">{mode==="pregame"&&data.formLast5!=null?<span className={"psr-form-badge "+((data.formChangePct??0)<0?"negative":"positive")}>{format(data.formLast5)} {data.formChangePct==null?"":(data.formChangePct>=0?"+":"")+data.formChangePct.toFixed(1)+"%"}</span>:<span className="psr-muted">—</span>}</div>
  </div>;
}
