import type { ReactNode } from "react";
import "./style.css";
export const metadata={title:"NBA Player Projections",description:"Pregame NBA player projections"};
export default function RootLayout({children}:{children:ReactNode}){return <html lang="en"><body><header><strong>NBA PLAYER PROJECTIONS</strong><nav><a href="/">Games</a><a href="/projections">Projections</a><a href="/accuracy">Accuracy</a><a href="/upload">Upload</a><a href="/settings">Settings</a></nav></header>{children}</body></html>}
