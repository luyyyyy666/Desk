import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "我的师傅 Learning OS",
  description: "High-fidelity static Learning OS prototype for question generation and practice.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
