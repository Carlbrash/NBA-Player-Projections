import type { ReactNode } from "react";
import "./style.css";
export const metadata = {title:"NBA Player Projections",description:"Pregame NBA statistical projections"};
export default function RootLayout({children}:{children:ReactNode}) {
 return <html lang="en"><body><header><strong>NBA PLAYER PROJECTIONS</strong><nav><a href="/">Today</a><a href="/accuracy">Accuracy</a><a href="/upload">Upload</a><a href="/settings">Settings</a></nav></header>{children}</body></html>;
}
