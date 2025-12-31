import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { getAuthToken, getCurrentUser, authenticatedFetch } from '../utils/auth';
import ProfileEditor from '../components/onboarding/profile-editor';

export default function DashboardPage() {
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const history = useHistory();

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);

    const token = getAuthToken();
    if (!token) {
      history.push('/auth/signin');
      return;
    }

    fetchProfile();
  }, [history]);

  const fetchProfile = async () => {
    try {
      const response = await authenticatedFetch('/api/profile/me');

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Failed to fetch profile');
      }

      const profileData = await response.json();
      setProfile(profileData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Dashboard" description="Your profile dashboard">
        <div className="container margin-vert--lg">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <div className="text--center padding--vert--xl">
                <div className="loading loading--sm"></div>
                <p>Loading your profile...</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Dashboard" description="Your profile dashboard">
        <div className="container margin-vert--lg">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <div className="alert alert--danger">
                <h3>Error</h3>
                <p>{error}</p>
                <button
                  className="button button--primary"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const [isEditing, setIsEditing] = useState(false);

  const handleSaveProfile = async (updatedProfile) => {
    try {
      const response = await authenticatedFetch('/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedProfile),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Failed to save profile');
      }

      // Update local state
      setProfile(updatedProfile);
      setIsEditing(false);
    } catch (err) {
      console.error('Error saving profile:', err);
      alert(`Error saving profile: ${err.message}`);
    }
  };

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <Layout title="Edit Profile" description="Edit your profile information">
        <div className="container margin-vert--lg">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <div className="card">
                <div className="card__header">
                  <h2>Edit Profile</h2>
                  <p>Update your profile information</p>
                </div>
                <div className="card__body">
                  {profile ? (
                    <ProfileEditor
                      profile={profile}
                      onSave={handleSaveProfile}
                      onCancel={handleCancelEdit}
                    />
                  ) : (
                    <div className="text--center padding--vert--xl">
                      <div className="loading loading--sm"></div>
                      <p>Loading profile data...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard" description="Your profile dashboard">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <div className="card">
              <div className="card__header">
                <h2>Dashboard</h2>
                <p>Welcome back, {user?.name || user?.email}!</p>
              </div>
              <div className="card__body">
                <h3>Your Profile Information</h3>

                <div className="row margin-bottom--lg">
                  <div className="col col--6">
                    <h4>Personal Details</h4>
                    <ul className="clean-list">
                      <li><strong>Email:</strong> {user?.email}</li>
                      <li><strong>Name:</strong> {user?.name || 'Not provided'}</li>
                    </ul>
                  </div>
                  <div className="col col--6">
                    <h4>Background Information</h4>
                    <ul className="clean-list">
                      <li><strong>Programming Level:</strong> {profile?.programmingLevel || 'Not set'}</li>
                      <li><strong>Learning Goal:</strong> {profile?.learningGoal || 'Not set'}</li>
                    </ul>
                  </div>
                </div>

                <div className="row margin-bottom--lg">
                  <div className="col col--6">
                    <h4>Known Languages</h4>
                    <div className="tag-pills">
                      {profile?.languages && profile.languages.length > 0 ? (
                        profile.languages.map((lang, index) => (
                          <span key={index} className="tag tag--info margin-right--sm">
                            {lang}
                          </span>
                        ))
                      ) : (
                        <em>No languages added</em>
                      )}
                    </div>
                  </div>
                  <div className="col col--6">
                    <h4>Tools Used</h4>
                    <div className="tag-pills">
                      {profile?.tools && profile.tools.length > 0 ? (
                        profile.tools.map((tool, index) => (
                          <span key={index} className="tag tag--info margin-right--sm">
                            {tool}
                          </span>
                        ))
                      ) : (
                        <em>No tools added</em>
                      )}
                    </div>
                  </div>
                </div>

                <div className="row">
                  <div className="col col--6">
                    <h4>Hardware Specifications</h4>
                    <ul className="clean-list">
                      <li><strong>RAM:</strong> {profile?.ram || 'Not set'}</li>
                      <li><strong>Processor:</strong> {profile?.processor || 'Not set'}</li>
                      <li><strong>GPU:</strong> {profile?.gpu || 'Not set'}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="card__footer">
                <div className="button-group">
                  <button
                    className="button button--secondary"
                    onClick={handleEditClick}
                  >
                    Edit Profile
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}