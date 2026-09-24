import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InsightOS — Research Intelligence Platform",
  description: "AI-Powered Qualitative Research Intelligence Platform V1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-background text-foreground antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
