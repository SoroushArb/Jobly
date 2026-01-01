import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Jobly - AI Job Hunter Agent",
  description: "Upload your CV and manage your job search profile",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
