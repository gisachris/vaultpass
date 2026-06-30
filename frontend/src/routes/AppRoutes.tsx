import { Routes, Route, Navigate } from 'react-router-dom';
import { Home } from '../pages/Home';
import { SignUpPage } from '../pages/SignUpPage';
import { SignInPage } from '../pages/SignInPage';
import { DocumentsPage } from '../pages/DocumentsPage';
import { TrustedContactsPage } from '../pages/TrustedContactsPage';
import { NotificationsPage } from '../features/notifications/pages/NotificationsPage';
import { SharedAccessPage } from '../pages/SharedAccessPage';
import { SharedDocumentView } from '../pages/SharedDocumentView';
import { SettingsPage } from '../pages/SettingsPage';
import { ReceivedDocumentsPage } from '../pages/ReceivedDocumentsPage';
import { FamilyHubPage } from '../features/family/pages/FamilyHubPage';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const LoadingScreen = () => (
  <div style={{
    display: 'flex', justifyContent: 'center', alignItems: 'center',
    minHeight: '100vh', backgroundColor: '#ffffff',
  }}>
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      gap: '16px', padding: '32px 36px', borderRadius: '24px',
      boxShadow: '0 28px 60px rgba(15, 23, 42, 0.08)',
    }}>
      <div style={{
        width: '40px', height: '40px', borderRadius: '50%',
        border: '4px solid #e2e8f0', borderTopColor: '#2c3e50',
        animation: 'spin 1s linear infinite',
      }} />
      <div style={{ color: '#0f172a', fontSize: '1rem', fontWeight: 600 }}>
        Loading secure session...
      </div>
    </div>
  </div>
);

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function PublicOnlyRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  if (user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/"                   element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/dashboard"          element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/documents"          element={<ProtectedRoute><DocumentsPage /></ProtectedRoute>} />
      <Route path="/trusted-contacts"   element={<ProtectedRoute><TrustedContactsPage /></ProtectedRoute>} />
      <Route path="/family"             element={<ProtectedRoute><FamilyHubPage /></ProtectedRoute>} />
      <Route path="/shared-access"      element={<ProtectedRoute><SharedAccessPage /></ProtectedRoute>} />
      <Route path="/received-documents" element={<ProtectedRoute><ReceivedDocumentsPage /></ProtectedRoute>} />
      <Route path="/notifications"      element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
      <Route path="/settings"           element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="/signup"             element={<PublicOnlyRoute><SignUpPage /></PublicOnlyRoute>} />
      <Route path="/login"              element={<PublicOnlyRoute><SignInPage /></PublicOnlyRoute>} />
      <Route path="/shared/:token"      element={<SharedDocumentView />} />
      <Route path="*"                   element={<Navigate to="/" replace />} />
    </Routes>
  );
}
