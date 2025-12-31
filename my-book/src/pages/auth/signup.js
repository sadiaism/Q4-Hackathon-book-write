import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();

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
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || 'Signup failed');
      }

      // Store token and user info in localStorage
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify({
        id: data.userId,
        email: data.email,
        name: data.name
      }));

      // Redirect to onboarding after successful signup
      history.push('/auth/onboarding');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Sign Up" description="Create your account">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--6 col--offset-3">
            <div className="card">
              <div className="card__header">
                <h2>Sign Up</h2>
              </div>
              <div className="card__body">
                {error && (
                  <div className="alert alert--danger">
                    {error}
                  </div>
                )}
                <form onSubmit={handleSubmit}>
                  <div className="margin-bottom--md">
                    <label htmlFor="name">Name</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="Enter your name"
                    />
                  </div>
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
                      minLength="6"
                    />
                  </div>
                  <div className="button-group button-group--block">
                    <button
                      type="submit"
                      className="button button--primary"
                      disabled={loading}
                    >
                      {loading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                  </div>
                </form>
              </div>
              <div className="card__footer">
                <p>
                  Already have an account? <a href="/auth/signin">Sign in</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}