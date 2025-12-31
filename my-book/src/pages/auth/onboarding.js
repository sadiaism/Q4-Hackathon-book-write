import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { getAuthToken, authenticatedFetch } from '../../utils/auth';

export default function OnboardingPage() {
  const [formData, setFormData] = useState({
    programmingLevel: '',
    languages: [],
    tools: [],
    ram: '',
    processor: '',
    gpu: '',
    learningGoal: ''
  });
  const [currentLanguage, setCurrentLanguage] = useState('');
  const [currentTool, setCurrentTool] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();

  // Check if user is authenticated
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      history.push('/auth/signin');
    }
  }, [history]);

  const handleAddLanguage = () => {
    if (currentLanguage.trim() && !formData.languages.includes(currentLanguage.trim())) {
      setFormData({
        ...formData,
        languages: [...formData.languages, currentLanguage.trim()]
      });
      setCurrentLanguage('');
    }
  };

  const handleRemoveLanguage = (language) => {
    setFormData({
      ...formData,
      languages: formData.languages.filter(lang => lang !== language)
    });
  };

  const handleAddTool = () => {
    if (currentTool.trim() && !formData.tools.includes(currentTool.trim())) {
      setFormData({
        ...formData,
        tools: [...formData.tools, currentTool.trim()]
      });
      setCurrentTool('');
    }
  };

  const handleRemoveTool = (tool) => {
    setFormData({
      ...formData,
      tools: formData.tools.filter(t => t !== tool)
    });
  };

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
      const response = await authenticatedFetch('/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Failed to save profile');
      }

      // Redirect to home after successful onboarding
      history.push('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Onboarding" description="Complete your profile">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <div className="card">
              <div className="card__header">
                <h2>Welcome! Please complete your profile</h2>
                <p className="text--center">Help us personalize your experience</p>
              </div>
              <div className="card__body">
                {error && (
                  <div className="alert alert--danger">
                    {error}
                  </div>
                )}
                <form onSubmit={handleSubmit}>
                  <div className="row">
                    <div className="col col--6">
                      <div className="margin-bottom--md">
                        <label htmlFor="programmingLevel">Programming Level *</label>
                        <select
                          id="programmingLevel"
                          name="programmingLevel"
                          value={formData.programmingLevel}
                          onChange={handleChange}
                          className="form-control"
                          required
                        >
                          <option value="">Select your level</option>
                          <option value="beginner">Beginner</option>
                          <option value="intermediate">Intermediate</option>
                          <option value="advanced">Advanced</option>
                          <option value="expert">Expert</option>
                        </select>
                      </div>

                      <div className="margin-bottom--md">
                        <label htmlFor="ram">RAM *</label>
                        <input
                          type="text"
                          id="ram"
                          name="ram"
                          value={formData.ram}
                          onChange={handleChange}
                          className="form-control"
                          placeholder="e.g., 8GB, 16GB, 32GB"
                          required
                        />
                      </div>

                      <div className="margin-bottom--md">
                        <label htmlFor="processor">Processor *</label>
                        <input
                          type="text"
                          id="processor"
                          name="processor"
                          value={formData.processor}
                          onChange={handleChange}
                          className="form-control"
                          placeholder="e.g., Intel i5, AMD Ryzen 7"
                          required
                        />
                      </div>

                      <div className="margin-bottom--md">
                        <label htmlFor="gpu">GPU *</label>
                        <input
                          type="text"
                          id="gpu"
                          name="gpu"
                          value={formData.gpu}
                          onChange={handleChange}
                          className="form-control"
                          placeholder="e.g., Integrated, RTX 3060"
                          required
                        />
                      </div>
                    </div>

                    <div className="col col--6">
                      <div className="margin-bottom--md">
                        <label htmlFor="learningGoal">Learning Goal *</label>
                        <textarea
                          id="learningGoal"
                          name="learningGoal"
                          value={formData.learningGoal}
                          onChange={handleChange}
                          className="form-control"
                          placeholder="What do you hope to learn?"
                          rows="4"
                          required
                        />
                      </div>

                      <div className="margin-bottom--md">
                        <label>Known Languages *</label>
                        <div className="input-group">
                          <input
                            type="text"
                            value={currentLanguage}
                            onChange={(e) => setCurrentLanguage(e.target.value)}
                            className="form-control"
                            placeholder="Add a programming language"
                          />
                          <button
                            type="button"
                            className="button button--secondary"
                            onClick={handleAddLanguage}
                          >
                            Add
                          </button>
                        </div>
                        <div className="tag-pills margin-top--sm">
                          {formData.languages.map((language, index) => (
                            <span key={index} className="tag tag--sm tag--info margin-right--sm">
                              {language}
                              <button
                                type="button"
                                className="clean-btn margin-left--sm"
                                onClick={() => handleRemoveLanguage(language)}
                              >
                                ×
                              </button>
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="margin-bottom--md">
                        <label>Tools Used *</label>
                        <div className="input-group">
                          <input
                            type="text"
                            value={currentTool}
                            onChange={(e) => setCurrentTool(e.target.value)}
                            className="form-control"
                            placeholder="Add a tool"
                          />
                          <button
                            type="button"
                            className="button button--secondary"
                            onClick={handleAddTool}
                          >
                            Add
                          </button>
                        </div>
                        <div className="tag-pills margin-top--sm">
                          {formData.tools.map((tool, index) => (
                            <span key={index} className="tag tag--sm tag--info margin-right--sm">
                              {tool}
                              <button
                                type="button"
                                className="clean-btn margin-left--sm"
                                onClick={() => handleRemoveTool(tool)}
                              >
                                ×
                              </button>
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="button-group button-group--block margin-top--lg">
                    <button
                      type="submit"
                      className="button button--primary"
                      disabled={loading || !formData.programmingLevel || !formData.ram || !formData.processor || !formData.gpu || !formData.learningGoal || formData.languages.length === 0 || formData.tools.length === 0}
                    >
                      {loading ? 'Saving Profile...' : 'Complete Onboarding'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}