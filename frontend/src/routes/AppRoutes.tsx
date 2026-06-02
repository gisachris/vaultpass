import { Routes, Route, Navigate } from 'react-router-dom';
import { Home } from '../pages/Home';
import { SignUpPage } from '../pages/SignUpPage';
import { SignInPage } from '../pages/SignInPage';
import { DashboardPage } from '../pages/DashboardPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/login" element={<SignInPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
