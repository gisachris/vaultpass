import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { sendVerificationEmail } from '../services/emailService';
import './AuthPage.css';

export function SignUpPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    terms: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
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
      const data = await register({
        full_name: formData.fullName,
        email: formData.email,
        password: formData.password,
      });

      const verificationLink = `${window.location.origin}/verify?token=${data.verification_token}`;

      toast.promise(
        sendVerificationEmail(formData.email, formData.fullName, verificationLink),
        {
          loading: 'Sending verification email...',
          success: 'Verification email sent! Please check your inbox.',
          error: 'Failed to send verification email.',
        }
      );

      setVerificationSent(true);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };


  return (
    <div className="auth-page-wrapper">
      <div className="auth-container">
        {/* Left Column - Branding & Context */}
        <div className="auth-left-column">
          <div className="auth-left-decorative auth-left-top" />
          <div className="auth-left-decorative auth-left-bottom" />

          <div className="auth-left-content auth-left-main">
            <div className="auth-brand-header">
              <span className="material-symbols-outlined auth-brand-icon">shield</span>
              <span className="auth-brand-title">VaultPass</span>
            </div>
            <h1 className="auth-left-heading">
              Your legacy, <br />
              <span className="auth-accent-text">secured for life.</span>
            </h1>
            <p className="auth-left-description">
              Join thousands of families who trust VaultPass to manage their most sensitive life documents with
              enterprise-grade security and professional care.
            </p>
          </div>

          <div className="auth-left-content auth-left-footer">
            <div className="auth-social-proof">
              <div className="auth-avatars">
                <img
                  alt="User 1"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuDcFZ4uGDjoZgGUwMPzwxll-vX0PKUsMFq_fxFUXsDDJTI0nPh8Swg8bhh0FIksqWi2-Buhy5PtNFUkxThOkA-CbYRUEr1UmkLMHqbwksFZqb4kdg4HAVsK5eUJjMoEEtUp9vmyE0jG-j-F00AIQi1nLKmxqUx7NlJpQ1q4DqcVqmfYQ8_9mATMX57Nslcp_Vd6mdQjRo9kmi7QsKhuwtqb6Jfgg8_3Yx-04kUAG-GMLZFm8wp-amGwGn9LGezRK2CBvaIgrjVwCMOA"
                  className="auth-avatar-img"
                />
                <img
                  alt="User 2"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAXCk6qzcwtzmM5KTy8RIzRmddgLaLfPqTnB8moDhWloUoeZte1F0hSKy8IIdiRkU7eOdRmEFzvC_q0KoHCmc9JxCPJ5gBTiKiLz8_B_IG-1ajUx_w4qfnIS6pt9MZ-wPLownLO94shNyMKT9BDC8hF6J8wMyFeoaJ-tgfIQ9EEk3JUUjkmMK_LPwH2WGsCxaGdgrSi4-CoieS-Ie-RC7C7olO0l1Ibxj1LWCFqCkJI-W5q74hhxxSzpXPuZ35mjXKXGoPYix7tVRuw"
                  className="auth-avatar-img"
                />
                <img
                  alt="User 3"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuBG1j2cUhYNEheKbGY51LQW6aZB-Bloug-w7Y1OpTEjCGh0l3mk4XBgDsSf7BRY3b5RLP2ZB4TlMXHSIpcx58G5BBEUV0yMTbyGjzqkqdkSNu1yVo7CuhrwNTi58xi0j_cDsQVicYlrnVkRwYRMKh7yaRGJwOaA_iAA32uAuwhUsidsMWoszxKJLjfsiDtFerCXnIirEovcMTNW9leS0HQSKNAjWUb_ex6OIcJnFpVWkFagPDhk1vV2CzJt7E_4oJ9shJRtSvMXgPVd"
                  className="auth-avatar-img"
                />
              </div>
              <span className="auth-trust-text">Trusted by 2,000+ members</span>
            </div>
          </div>
        </div>

        {/* Right Column - Form */}
        <div className="auth-right-column">
          {/* Mobile Logo */}
          <div className="auth-mobile-logo">
            <span className="material-symbols-outlined auth-logo-icon">shield</span>
            <span className="auth-logo-text">VaultPass</span>
          </div>

          <div className="auth-form-container">
            {verificationSent ? (
              <div className="auth-verification-sent" style={{ textAlign: 'center', padding: '20px 0' }}>
                <span className="material-symbols-outlined auth-verification-icon" style={{ fontSize: '64px', color: '#10B981', marginBottom: '16px' }}>
                  mark_email_read
                </span>
                <h2 className="auth-form-title">Verify Your Email</h2>
                <p className="auth-form-subtitle" style={{ margin: '16px 0 24px', lineHeight: '1.6' }}>
                  We've sent a verification link to <strong style={{ color: 'var(--text-primary, #ffffff)' }}>{formData.email}</strong>.
                  Please click the link in the email to activate your account.
                </p>
                <button className="auth-submit-button" onClick={() => navigate('/login')}>
                  Go to Sign In
                </button>
              </div>
            ) : (
              <>
                <div className="auth-form-header">
                  <h2 className="auth-form-title">Create Account</h2>
                  <p className="auth-form-subtitle">Secure your sensitive documents today.</p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                  {/* Full Name Field */}
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="fullName">
                      FULL NAME
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">person</span>
                      <input
                        className="auth-input"
                        id="fullName"
                        name="fullName"
                        placeholder="John Doe"
                        required
                        type="text"
                        value={formData.fullName}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  {/* Email Field */}
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="email">
                      EMAIL ADDRESS
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">mail</span>
                      <input
                        className="auth-input"
                        id="email"
                        name="email"
                        placeholder="name@company.com"
                        required
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="auth-form-group">
                    <label className="auth-form-label" htmlFor="password">
                      PASSWORD
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
                      CONFIRM PASSWORD
                    </label>
                    <div className="auth-input-wrapper">
                      <span className="material-symbols-outlined auth-input-icon">lock_reset</span>
                      <input
                        className="auth-input"
                        id="confirmPassword"
                        name="confirmPassword"
                        placeholder="••••••••"
                        required
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                      />
                      <button
                        className="auth-input-toggle"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        type="button"
                      >
                        <span className="material-symbols-outlined">
                          {showConfirmPassword ? 'visibility_off' : 'visibility'}
                        </span>
                      </button>
                    </div>
                  </div>

                  {/* Terms & Conditions */}
                  <div className="auth-checkbox-group">
                    <input
                      className="auth-checkbox"
                      id="terms"
                      name="terms"
                      required
                      type="checkbox"
                      checked={formData.terms}
                      onChange={handleInputChange}
                    />
                    <label className="auth-checkbox-label" htmlFor="terms">
                      I agree to the{' '}
                      <a className="auth-link auth-link-bold" href="#">
                        Terms of Service
                      </a>{' '}
                      and{' '}
                      <a className="auth-link auth-link-bold" href="#">
                        Privacy Policy
                      </a>
                      .
                    </label>
                  </div>

                  {/* Submit Button */}
                  <button className="auth-submit-button" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating Account...' : 'Create Account'}
                  </button>
                </form>

                {/* Navigation Link */}
                <div className="auth-footer-link">
                  <p className="auth-footer-text">
                    Already have an account?{' '}
                    <a className="auth-link auth-link-bold" href="/login">
                      Sign In
                    </a>
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Trust Indicators */}
          <div className="auth-trust-badges">
            <div className="auth-trust-badge">
              <span className="material-symbols-outlined auth-badge-icon">lock</span>
              <span className="auth-badge-text">AES-256 ENCRYPTION</span>
            </div>
            <div className="auth-trust-badge">
              <span className="material-symbols-outlined auth-badge-icon">verified_user</span>
              <span className="auth-badge-text">GDPR COMPLIANT</span>
            </div>
            <div className="auth-trust-badge">
              <span className="material-symbols-outlined auth-badge-icon">cloud_done</span>
              <span className="auth-badge-text">ISO 27001</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
