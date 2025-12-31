import React, { useState } from 'react';

export default function ProfileEditor({ profile, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    programmingLevel: profile?.programmingLevel || '',
    languages: profile?.languages || [],
    tools: profile?.tools || [],
    ram: profile?.ram || '',
    processor: profile?.processor || '',
    gpu: profile?.gpu || '',
    learningGoal: profile?.learningGoal || ''
  });
  const [currentLanguage, setCurrentLanguage] = useState('');
  const [currentTool, setCurrentTool] = useState('');

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

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="row">
        <div className="col col--6">
          <div className="margin-bottom--md">
            <label htmlFor="programmingLevel">Programming Level</label>
            <select
              id="programmingLevel"
              name="programmingLevel"
              value={formData.programmingLevel}
              onChange={handleChange}
              className="form-control"
            >
              <option value="">Select your level</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>

          <div className="margin-bottom--md">
            <label htmlFor="ram">RAM</label>
            <input
              type="text"
              id="ram"
              name="ram"
              value={formData.ram}
              onChange={handleChange}
              className="form-control"
              placeholder="e.g., 8GB, 16GB, 32GB"
            />
          </div>

          <div className="margin-bottom--md">
            <label htmlFor="processor">Processor</label>
            <input
              type="text"
              id="processor"
              name="processor"
              value={formData.processor}
              onChange={handleChange}
              className="form-control"
              placeholder="e.g., Intel i5, AMD Ryzen 7"
            />
          </div>

          <div className="margin-bottom--md">
            <label htmlFor="gpu">GPU</label>
            <input
              type="text"
              id="gpu"
              name="gpu"
              value={formData.gpu}
              onChange={handleChange}
              className="form-control"
              placeholder="e.g., Integrated, RTX 3060"
            />
          </div>
        </div>

        <div className="col col--6">
          <div className="margin-bottom--md">
            <label htmlFor="learningGoal">Learning Goal</label>
            <textarea
              id="learningGoal"
              name="learningGoal"
              value={formData.learningGoal}
              onChange={handleChange}
              className="form-control"
              placeholder="What do you hope to learn?"
              rows="4"
            />
          </div>

          <div className="margin-bottom--md">
            <label>Known Languages</label>
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
                className="button button--secondary button--sm"
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
            <label>Tools Used</label>
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
                className="button button--secondary button--sm"
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
          type="button"
          className="button button--secondary"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="button button--primary"
          disabled={!formData.programmingLevel || !formData.ram || !formData.processor || !formData.gpu || !formData.learningGoal || formData.languages.length === 0 || formData.tools.length === 0}
        >
          Save Profile
        </button>
      </div>
    </form>
  );
}