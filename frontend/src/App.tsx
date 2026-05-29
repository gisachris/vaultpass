import { AppRoutes } from './routes/AppRoutes';

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="container">
          <h1>Vaultpass</h1>
          <p>Your secure password manager frontend.</p>
        </div>
      </header>
      <main className="app-main">
        <div className="container">
          <AppRoutes />
        </div>
      </main>
    </div>
  );
}

export default App;
