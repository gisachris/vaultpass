import { Button } from '../components/ui/Button';

export function Home() {
  return (
    <section className="home-page">
      <h2>Welcome to Vaultpass</h2>
      <p>
        Vaultpass is a secure password manager interface built with React, TypeScript,
        and Vite. Start by connecting your backend APIs and extending this app with your
        authentication flow.
      </p>
      <div className="home-actions">
        <Button type="button">Get Started</Button>
      </div>
    </section>
  );
}
