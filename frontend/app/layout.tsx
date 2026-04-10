import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "DeFi Research Console",
  description: "Streaming DeFi analysis dashboard",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="bg-mesh" />
        {children}
      </body>
    </html>
  );
}
