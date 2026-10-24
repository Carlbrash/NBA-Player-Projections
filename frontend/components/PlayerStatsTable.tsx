import PlayerStatRow,{type PlayerStatRowData} from "./PlayerStatRow";
import "./PlayerStatsTable.css";
export default function PlayerStatsTable({rows,mode}:{rows:PlayerStatRowData[];mode:"pregame"|"final"}){
 return <div className="psr-table-scroll"><div className="psr-table">
   <div className="psr-header"><span>PLAYER</span><span>PTS</span><span>REB</span><span>AST</span><span>3PM</span><span>PRA</span><span>{mode==="pregame"?"FORM L5":"FORM L5"}</span></div>
   {rows.map(row=><PlayerStatRow key={row.gameId+"-"+row.playerId} data={row} mode={mode}/>)}
   {rows.length===0&&<p className="psr-empty">No player statistics available for this selection.</p>}
 </div></div>;
}
