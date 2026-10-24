import "./StartingLineups.css";
export type Starter={playerId:number;name:string;jerseyNumber:number|null;photoUrl:string|null;position:string|null;actualPts:number|null};
export type StartingTeam={code:string;name:string;logoUrl:string|null;primaryColor:string;secondaryColor:string;record:string|null;side:"away"|"home";starters:Starter[]};
export default function StartingLineups({away,home,status}:{away:StartingTeam;home:StartingTeam;status:"confirmed"|"projected"|"historical"|"unavailable"}){
 const historical=status==="historical";
 return <section className="sl-panel" aria-label="Starting lineups">
  <div className="sl-title"><h2>STARTING LINEUPS</h2><span className={"sl-status "+status}>{historical?"HISTORICAL":status.toUpperCase()}</span></div>
  <div className="sl-teams">{[away,home].map(team=><div key={team.side} className="sl-team" style={{"--team-primary":team.primaryColor,"--team-secondary":team.secondaryColor} as React.CSSProperties}>
    <div className="sl-team-header">{team.logoUrl&&<img src={team.logoUrl} alt="" />}<div><strong>{team.code} ({team.side.toUpperCase()})</strong>{team.record&&<small>{team.record}</small>}</div></div>
    <div className="sl-roster">{team.starters.map(player=><a key={player.playerId} href={`/players/${player.playerId}`} className="sl-player">
      <span className="sl-number">{player.jerseyNumber??"—"}</span>
      <span className="sl-photo">{player.photoUrl?<img src={player.photoUrl} alt="" loading="lazy"/>:<span>NBA</span>}</span>
      <span className="sl-name">{player.name}</span>
      <span className="sl-role">{historical?(player.actualPts==null?"—":player.actualPts+" PTS"):(player.position||"—")}</span>
    </a>)}
    {team.starters.length===0&&<div className="sl-empty">Starting five not confirmed</div>}</div>
  </div>)}</div>
 </section>
}
