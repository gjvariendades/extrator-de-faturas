async function getHealth(apiUrl: string): Promise<string> {
  try {
    const response = await fetch(`${apiUrl}/health`, { cache: 'no-store' });
    if (!response.ok) return 'offline';
    const data = (await response.json()) as { status?: string };
    return data.status ?? 'unknown';
  } catch {
    return 'offline';
  }
}

export default async function Home() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  const status = await getHealth(apiUrl);

  return (
    <main style={{ fontFamily: 'sans-serif', margin: '2rem' }}>
      <h1>Extrator de Faturas</h1>
      <p>API: {apiUrl}</p>
      <p>Healthcheck: {status}</p>
      <p>Usuário seed: admin@demo.com / admin123</p>
    </main>
  );
}
