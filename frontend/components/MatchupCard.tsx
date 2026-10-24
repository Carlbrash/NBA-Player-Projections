import "./MatchupCard.css";
export type MatchupCardData = {
 id:string|number; awayCode:string;homeCode:string;
 awayLogo:string;homeLogo:string;
 awayWins:number|null;awayLosses:number|null;
 homeWins:number|null;homeLosses:number|null;
 startTime:string; // localized display string
 status:"scheduled"|"final";
 awayScore?:number|null;homeScore?:number|null;
 h2hAwayWins:number;h2hHomeWins:number;h2hGames:number;
};
const record=(w:number|null,l:number|null)=>w==null||l==null?"—":w+"–"+l;
export default function MatchupCard({game,selected=false,onSelect}:{
 game:MatchupCardData;selected?:boolean;onSelect?:(id:string|number)=>void
}){
 const final=game.status==="final";
 const hasScore=final&&game.awayScore!=null&&game.homeScore!=null;
 return <button type="button" className={"nba-matchup "+(selected?"is-selected":"")}
 aria-pressed={selected} aria-label={game.awayCode+" at "+game.homeCode}
 onClick={()=>onSelect?.(game.id)}>
  <div className="nba-team">
   <img src={game.awayLogo} alt="" className="nba-logo" loading="lazy"/>
   <strong>{game.awayCode}</strong>
   <span className="nba-record">{record(game.awayWins,game.awayLosses)}</span>
  </div>
  <div className="nba-center">
   <span className={"nba-top "+(hasScore?"nba-final":"")}>{hasScore?"FINAL":game.startTime}</span>
   <span className="nba-vs">{hasScore?game.awayScore+" : "+game.homeScore:"VS"}</span>
   <span className="nba-h2h">{game.h2hGames===0?"NO H2H":game.h2hAwayWins+"–"+game.h2hHomeWins}</span>
   <span className="nba-h2h-label">H2H · THIS SEASON</span>
  </div>
  <div className="nba-team">
   <img src={game.homeLogo} alt="" className="nba-logo" loading="lazy"/>
   <strong>{game.homeCode}</strong>
   <span className="nba-record">{record(game.homeWins,game.homeLosses)}</span>
  </div>
 </button>
}
