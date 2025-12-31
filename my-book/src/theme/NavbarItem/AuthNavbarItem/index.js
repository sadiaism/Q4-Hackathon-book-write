import React, { useState, useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { isAuthenticated, getCurrentUser, removeAuthToken } from '../../../utils/auth';

// Custom navbar item component for authentication
const AuthNavbarItem = (props) => {
  const location = useLocation();
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    user: null
  });
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'

  useEffect(() => {
    // Check auth status on mount and route changes
    const checkAuth = () => {
      const authenticated = isAuthenticated();
      const user = getCurrentUser();
      setAuthState({
        isAuthenticated: authenticated,
        user: user
      });
    };

    checkAuth();

    // Listen for storage events to handle auth changes across tabs
    if (typeof window === 'undefined') return;

    const handleStorageChange = (e) => {
      if (e.key === 'authToken') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [location.pathname]);

  const handleSignOut = (e) => {
    e.preventDefault();
    if (typeof window === 'undefined') return;
    // Remove auth token without page refresh
    removeAuthToken();
    // Update state immediately
    setAuthState({
      isAuthenticated: false,
      user: null
    });
    // Trigger storage event for other components
    window.dispatchEvent(new Event('storage'));
  };

  const openSignIn = (e) => {
    e.preventDefault();
    setAuthMode('signin');
    setShowAuthModal(true);
  };

  const openSignUp = (e) => {
    e.preventDefault();
    setAuthMode('signup');
    setShowAuthModal(true);
  };

  const closeAuthModal = () => {
    setShowAuthModal(false);
  };

  // Apply any className from props
  const className = [props.className, 'navbar__item']
    .filter(Boolean)
    .join(' ');

  if (authState.isAuthenticated) {
    // Show user dropdown when authenticated
    return (
      <div className={`${className} dropdown dropdown--hoverable dropdown--right`.trim()}>
        <a className="navbar__link">
          {authState.user?.name || authState.user?.email || 'Account'} {'\u25BE'}
        </a>
        <ul className="dropdown__menu">
          <li><a className="dropdown__link" href="/dashboard">Dashboard</a></li>
          <li><a className="dropdown__link" href="#" onClick={handleSignOut}>Sign Out</a></li>
        </ul>
      </div>
    );
  } else {
    // Show sign in/up when not authenticated
    return (
      <>
        <div className={className}>
          <a className="navbar__link" href="#" onClick={openSignIn} style={{ marginRight: '10px' }}>
            Sign In
          </a>
          <a className="button button--primary button--sm" href="#" onClick={openSignUp}>
            Sign Up
          </a>
        </div>
        {showAuthModal && (
          <AuthModalInline
            mode={authMode}
            onClose={closeAuthModal}
            onAuthSuccess={() => {
              closeAuthModal();
              // Refresh auth state
              const authenticated = isAuthenticated();
              const user = getCurrentUser();
              setAuthState({
                isAuthenticated: authenticated,
                user: user
              });
            }}
          />
        )}
      </>
    );
  }
};

// Inline Modal Component
const AuthModalInline = ({ mode, onClose, onAuthSuccess }) => {
  const { siteConfig } = useDocusaurusContext();
  const [formMode, setFormMode] = useState(mode);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiUrl = siteConfig.customFields?.apiUrl || 'http://localhost:8000';
      const endpoint = formMode === 'signin' ? '/api/auth/signin' : '/api/auth/signup';

      if (formMode === 'signup') {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }
        if (!formData.name.trim()) {
          setError('Name is required');
          setLoading(false);
          return;
        }
      }

      const payload = formMode === 'signin'
        ? { email: formData.email, password: formData.password }
        : { email: formData.email, password: formData.password, name: formData.name };

      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Authentication failed');
      }

      if (typeof window !== 'undefined') {
        localStorage.setItem('authToken', data.access_token || data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        window.dispatchEvent(new Event('storage'));
      }

      onAuthSuccess();

      if (formMode === 'signin' && typeof window !== 'undefined') {
        window.location.href = '/dashboard';
      }
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setFormMode(formMode === 'signin' ? 'signup' : 'signin');
    setError('');
    setFormData({ email: '', password: '', name: '', confirmPassword: '' });
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: 'var(--ifm-background-color)',
          borderRadius: '8px',
          padding: '2rem',
          maxWidth: '450px',
          width: '90%',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'relative',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: 'var(--ifm-color-emphasis-600)',
          }}
        >
          &times;
        </button>

        <h2 style={{ marginBottom: '0.5rem' }}>
          {formMode === 'signin' ? 'Sign In' : 'Sign Up'}
        </h2>
        <p style={{ marginBottom: '1.5rem', color: 'var(--ifm-color-emphasis-700)' }}>
          {formMode === 'signin'
            ? 'Welcome back! Please sign in to continue.'
            : 'Create an account to get started.'}
        </p>

        <form onSubmit={handleSubmit}>
          {error && (
            <div
              style={{
                padding: '0.75rem',
                marginBottom: '1rem',
                backgroundColor: 'var(--ifm-color-danger-contrast-background)',
                color: 'var(--ifm-color-danger)',
                borderRadius: '4px',
                border: '1px solid var(--ifm-color-danger)',
              }}
            >
              {error}
            </div>
          )}

          {formMode === 'signup' && (
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid var(--ifm-color-emphasis-300)',
                  borderRadius: '4px',
                  fontSize: '1rem',
                }}
              />
            </div>
          )}

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid var(--ifm-color-emphasis-300)',
                borderRadius: '4px',
                fontSize: '1rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
              minLength={6}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid var(--ifm-color-emphasis-300)',
                borderRadius: '4px',
                fontSize: '1rem',
              }}
            />
          </div>

          {formMode === 'signup' && (
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
                minLength={6}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid var(--ifm-color-emphasis-300)',
                  borderRadius: '4px',
                  fontSize: '1rem',
                }}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: 'var(--ifm-color-primary)',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Please wait...' : (formMode === 'signin' ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <p>
            {formMode === 'signin'
              ? "Don't have an account? "
              : 'Already have an account? '}
            <button
              type="button"
              onClick={switchMode}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--ifm-color-primary)',
                cursor: 'pointer',
                textDecoration: 'underline',
                padding: 0,
              }}
            >
              {formMode === 'signin' ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthNavbarItem;