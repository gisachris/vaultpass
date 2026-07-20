import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import './AuthPage.css';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMessage, setErrorMessage] = useState('');
  const verificationAttempted = useRef(false);

  useEffect(() => {
    if (verificationAttempted.current) return;
    verificationAttempted.current = true;

    if (!token) {
      setStatus('error');
      setErrorMessage('Verification token is missing.');
      return;
    }

    async function verify() {
      try {
        await api.post(`/auth/verify-email?token=${token}`);
        setStatus('success');
      } catch (err: any) {
        setStatus('error');
        setErrorMessage(
          err.response?.data?.detail || 'Failed to verify email. The link may have expired.'
        );
      }
    }
    verify();
  }, [token]);

  return (
    <div className="auth-page-wrapper">
      <div className="auth-container" style={{ maxWidth: '480px', margin: '0 auto', display: 'block' }}>
        <div className="auth-right-column" style={{ width: '100%', minHeight: 'unset', padding: '40px 20px' }}>
          <div className="auth-mobile-logo" style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
            <span className="material-symbols-outlined auth-logo-icon">shield</span>
            <span className="auth-logo-text">VaultPass</span>
          </div>

          <div className="auth-form-container" style={{ textAlign: 'center' }}>
            {status === 'verifying' && (
              <div>
                <span className="material-symbols-outlined" style={{ fontSize: '64px', color: 'var(--accent-color)', animation: 'spin 2s linear infinite' }}>
                  sync
                </span>
                <h2 className="auth-form-title" style={{ marginTop: '16px' }}>Verifying Email</h2>
                <p className="auth-form-subtitle">Please wait while we activate your account...</p>
              </div>
            )}

            {status === 'success' && (
              <div>
                <span className="material-symbols-outlined" style={{ fontSize: '64px', color: '#10B981', marginBottom: '16px' }}>
                  verified
                </span>
                <h2 className="auth-form-title">Account Verified!</h2>
                <p className="auth-form-subtitle" style={{ margin: '16px 0 24px' }}>
                  Your email has been successfully verified. You can now access your secure vault.
                </p>
                <button className="auth-submit-button" onClick={() => navigate('/login')}>
                  Sign In
                </button>
              </div>
            )}

            {status === 'error' && (
              <div>
                <span className="material-symbols-outlined" style={{ fontSize: '64px', color: '#EF4444', marginBottom: '16px' }}>
                  error
                </span>
                <h2 className="auth-form-title">Verification Failed</h2>
                <p className="auth-form-subtitle" style={{ margin: '16px 0 24px', color: '#FDA4AF' }}>
                  {errorMessage}
                </p>
                <button className="auth-submit-button" onClick={() => navigate('/signup')}>
                  Back to Sign Up
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
