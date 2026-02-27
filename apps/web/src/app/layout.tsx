import type { ReactNode } from 'react';

export const metadata = {
  title: 'Extrator de Faturas',
  description: 'Monorepo base com API FastAPI + Next.js',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
