import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "html.ai - Embedding Identity to Components",
  description:
    "Create dynamic experiences based on user behavioral identity. Adaptive UI components that respond to who your users are.",
  keywords: [
    "html",
    "ai",
    "identity",
    "behavioral",
    "dynamic",
    "components",
    "personalization",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
