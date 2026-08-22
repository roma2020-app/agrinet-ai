import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgriNet AI",
  description:
    "BRICS Digital Agriculture Intelligence Network",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}