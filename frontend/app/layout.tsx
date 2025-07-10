// frontend/app/layout.tsx
import '../styles/globals.css';
import { ReactNode } from "react";
import ClientProviders from "./ClientProviders";

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
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}