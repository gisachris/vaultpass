import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { sendPasswordResetEmail } from '../services/emailService';
import { toast } from 'sonner';
import './AuthPage.css';

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await api.post('/auth/forgot-password', { email });
      const { reset_token } = response.data;
      const resetLink = `${window.location.origin}/reset-password?token=${reset_token}`;

      toast.promise(
        sendPasswordResetEmail(email, resetLink),
        {
          loading: 'Sending password recovery email...',
          success: 'Password reset link sent to your inbox!',
          error: 'Failed to send recovery email.',
        }
      );

      setEmailSent(true);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to request password reset.';
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-container" style={{ maxWidth: '480px', margin: '0 auto', display: 'block' }}>
        <div className="auth-right-column" style={{ width: '100%', minHeight: 'unset', padding: '40px 20px' }}>
          <div className="auth-mobile-logo" style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
            <span className="material-symbols-outlined auth-logo-icon">shield</span>
            <span className="auth-logo-text">VaultPass</span>
          </div>

          <div className="auth-form-container">
            {emailSent ? (
              <div style={{ textAlign: 'center' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '64px', color: '#10B981', marginBottom: '16px' }}>
                  mark_email_read
                </span>
                <h2 className="auth-form-title">Email Sent</h2>
                <p className="auth-form-subtitle" style={{ margin: '16px 0 24px', lineHeight: '1.6' }}>
                  We have sent instructions to reset your password to <strong style={{ color: 'white' }}>{email}</strong>.
                  Please check your inbox.
                </p>
                <button className="auth-submit-button" onClick={() => navigate('/login')}>
                  Back to Sign In
                </button>
              </div>
            ) : (
              <>
                <div className="auth-form-header" style={{ textAlign: 'center' }}>
                  <h2 className="auth-form-title">Forgot Password</h2>
                  <p className="auth-form-subtitle">Enter your email and we'll send you a password reset link.</p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="email">
                      EMAIL ADDRESS
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">mail</span>
                      <input
                        className="auth-input"
                        id="email"
                        placeholder="name@company.com"
                        required
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>
                  </div>

                  <button className="auth-submit-button" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Requesting Link...' : 'Send Reset Link'}
                  </button>
                </form>

                <div className="auth-footer-link" style={{ textAlign: 'center', marginTop: '24px' }}>
                  <a className="auth-link auth-link-bold" href="/login">
                    Back to Sign In
                  </a>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
