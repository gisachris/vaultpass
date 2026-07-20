import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { toast } from 'sonner';
import './AuthPage.css';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validatePasswordStrength = (pass: string) => {
    if (pass.length < 8) return 'Password must be at least 8 characters long';
    if (!/[A-Z]/.test(pass)) return 'Password must contain at least one uppercase letter';
    if (!/[a-z]/.test(pass)) return 'Password must contain at least one lowercase letter';
    if (!/\d/.test(pass)) return 'Password must contain at least one number';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      toast.error('Reset token is missing.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    const passwordError = validatePasswordStrength(formData.password);
    if (passwordError) {
      toast.error(passwordError);
      return;
    }

    setIsSubmitting(true);
    try {
      await api.post('/auth/reset-password', {
        token,
        new_password: formData.password,
      });
      toast.success('Password reset successfully!');
      setResetSuccess(true);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to reset password. The link may have expired.';
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
            {resetSuccess ? (
              <div style={{ textAlign: 'center' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '64px', color: '#10B981', marginBottom: '16px' }}>
                  task_alt
                </span>
                <h2 className="auth-form-title">Password Reset</h2>
                <p className="auth-form-subtitle" style={{ margin: '16px 0 24px' }}>
                  Your password has been successfully updated. You can now use your new password to sign in.
                </p>
                <button className="auth-submit-button" onClick={() => navigate('/login')}>
                  Go to Sign In
                </button>
              </div>
            ) : (
              <>
                <div className="auth-form-header" style={{ textAlign: 'center' }}>
                  <h2 className="auth-form-title">Reset Password</h2>
                  <p className="auth-form-subtitle">Choose a strong, secure new password for your account.</p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                  {/* Password Field */}
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="password">
                      NEW PASSWORD
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">lock</span>
                      <input
                        className="auth-input"
                        id="password"
                        name="password"
                        placeholder="••••••••"
                        required
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleInputChange}
                      />
                      <button
                        className="auth-input-toggle"
                        onClick={() => setShowPassword(!showPassword)}
                        type="button"
                      >
                        <span className="material-symbols-outlined">
                          {showPassword ? 'visibility_off' : 'visibility'}
                        </span>
                      </button>
                    </div>
                  </div>

                  {/* Confirm Password Field */}
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="confirmPassword">
                      CONFIRM NEW PASSWORD
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">lock_reset</span>
                      <input
                        className="auth-input"
                        id="confirmPassword"
                        name="confirmPassword"
                        placeholder="••••••••"
                        required
                        type={showPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  <button className="auth-submit-button" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Resetting Password...' : 'Reset Password'}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
