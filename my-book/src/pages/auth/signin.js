import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { useHistory, useLocation } from '@docusaurus/router';

export default function SigninPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();
  const location = useLocation();

  // Get redirect URL from query params or default to home
  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/signin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || 'Signin failed');
      }

      // Store token and user info in localStorage
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify({
        id: data.userId,
        email: data.email,
        name: data.name
      }));

      // Check if user has completed onboarding
      const profileResponse = await fetch('/api/profile/me', {
        headers: {
          'Authorization': `Bearer ${data.token}`,
        }
      });

      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        if (!profileData.completed) {
          // User hasn't completed onboarding, redirect to onboarding
          history.push('/auth/onboarding');
        } else {
          // User has completed onboarding, redirect to home
          history.push(from);
        }
      } else {
        // If profile doesn't exist or there's an error, redirect to onboarding
        history.push('/auth/onboarding');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Sign In" description="Sign in to your account">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--6 col--offset-3">
            <div className="card">
              <div className="card__header">
                <h2>Sign In</h2>
              </div>
              <div className="card__body">
                {error && (
                  <div className="alert alert--danger">
                    {error}
                  </div>
                )}
                <form onSubmit={handleSubmit}>
                  <div className="margin-bottom--md">
                    <label htmlFor="email">Email</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                  <div className="margin-bottom--md">
                    <label htmlFor="password">Password</label>
                    <input
                      type="password"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="Enter your password"
                      required
                    />
                  </div>
                  <div className="button-group button-group--block">
                    <button
                      type="submit"
                      className="button button--primary"
                      disabled={loading}
                    >
                      {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                  </div>
                </form>
              </div>
              <div className="card__footer">
                <p>
                  Don't have an account? <a href="/auth/signup">Sign up</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}