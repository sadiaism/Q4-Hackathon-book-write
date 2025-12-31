import React, { useEffect, useState } from 'react';
import { Redirect, useLocation } from '@docusaurus/router';
import { isAuthenticated } from '../../utils/auth';

export default function ProtectedRoute({ children, requireProfile = false }) {
  const [loading, setLoading] = useState(true);
  const [isAuth, setIsAuth] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      const auth = isAuthenticated();
      setIsAuth(auth);

      if (auth && requireProfile) {
        // Check if user has completed profile
        try {
          const token = localStorage.getItem('authToken');
          const response = await fetch('/api/profile/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
            }
          });

          if (response.ok) {
            const profileData = await response.json();
            setHasProfile(profileData.completed);
          } else {
            setHasProfile(false);
          }
        } catch (error) {
          console.error('Error checking profile:', error);
          setHasProfile(false);
        }
      }

      setLoading(false);
    };

    checkAuth();
  }, [requireProfile]);

  if (loading) {
    return (
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <div className="text--center padding--vert--xl">
              <div className="loading loading--sm"></div>
              <p>Checking authentication status...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuth) {
    // Redirect to signin with return URL
    return <Redirect to={`/auth/signin?returnUrl=${encodeURIComponent(location.pathname)}`} />;
  }

  if (requireProfile && !hasProfile) {
    // Redirect to onboarding
    return <Redirect to="/auth/onboarding" />;
  }

  // User is authenticated (and optionally has profile), render children
  return children;
}