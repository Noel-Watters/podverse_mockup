// frontend/app/layout.tsx

import '../styles/globals.css';
import { ReactNode } from "react";

export const metadata = {
  title: 'Podverse Admin',
  description: 'Admin dashboard for podcast management',
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-podverse-background text-podverse-text font-sans min-h-screen">
        {children}
      </body>
    </html>
  );
}
