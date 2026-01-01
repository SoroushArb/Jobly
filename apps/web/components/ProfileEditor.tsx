'use client';

import { useState, useEffect } from 'react';
import { UserProfile, SkillGroup, ExperienceRole, ExperienceBullet } from '@/types/profile';

interface ProfileEditorProps {
  initialProfile: UserProfile;
  onSave: (profile: UserProfile) => void;
  onCancel?: () => void;
}

export default function ProfileEditor({ initialProfile, onSave, onCancel }: ProfileEditorProps) {
  const [profile, setProfile] = useState<UserProfile>(initialProfile);
  const [saving, setSaving] = useState(false);

  // Update profile when initialProfile changes
  useEffect(() => {
    setProfile(initialProfile);
  }, [initialProfile]);

  const handleBasicInfoChange = (field: string, value: string) => {
    setProfile({ ...profile, [field]: value });
  };

  const handleLinksChange = (index: number, value: string) => {
    const newLinks = [...profile.links];
    newLinks[index] = value;
    setProfile({ ...profile, links: newLinks });
  };

  const addLink = () => {
    setProfile({ ...profile, links: [...profile.links, ''] });
  };

  const removeLink = (index: number) => {
    const newLinks = profile.links.filter((_, i) => i !== index);
    setProfile({ ...profile, links: newLinks });
  };

  const handleSkillGroupChange = (index: number, field: string, value: string | string[]) => {
    const newSkills = [...profile.skills];
    newSkills[index] = { ...newSkills[index], [field]: value };
    setProfile({ ...profile, skills: newSkills });
  };

  const handleSkillsChange = (groupIndex: number, value: string) => {
    const skills = value.split(',').map(s => s.trim()).filter(s => s);
    handleSkillGroupChange(groupIndex, 'skills', skills);
  };

  const addSkillGroup = () => {
    const newGroup: SkillGroup = { category: 'New Category', skills: [] };
    setProfile({ ...profile, skills: [...profile.skills, newGroup] });
  };

  const removeSkillGroup = (index: number) => {
    const newSkills = profile.skills.filter((_, i) => i !== index);
    setProfile({ ...profile, skills: newSkills });
  };

  const handleExperienceChange = (
    index: number,
    field: string,
    value: string | ExperienceBullet[] | string[]
  ) => {
    const newExperience = [...profile.experience];
    newExperience[index] = { ...newExperience[index], [field]: value };
    setProfile({ ...profile, experience: newExperience });
  };

  const handleBulletChange = (expIndex: number, bulletIndex: number, value: string) => {
    const newExperience = [...profile.experience];
    const newBullets = [...newExperience[expIndex].bullets];
    newBullets[bulletIndex] = { ...newBullets[bulletIndex], text: value };
    newExperience[expIndex].bullets = newBullets;
    setProfile({ ...profile, experience: newExperience });
  };

  const addBullet = (expIndex: number) => {
    const newExperience = [...profile.experience];
    newExperience[expIndex].bullets.push({ text: '', evidence_ref: undefined });
    setProfile({ ...profile, experience: newExperience });
  };

  const removeBullet = (expIndex: number, bulletIndex: number) => {
    const newExperience = [...profile.experience];
    newExperience[expIndex].bullets = newExperience[expIndex].bullets.filter(
      (_, i) => i !== bulletIndex
    );
    setProfile({ ...profile, experience: newExperience });
  };

  const addExperience = () => {
    const newRole: ExperienceRole = {
      company: '',
      title: '',
      dates: '',
      bullets: [],
      tech: [],
    };
    setProfile({ ...profile, experience: [...profile.experience, newRole] });
  };

  const removeExperience = (index: number) => {
    const newExperience = profile.experience.filter((_, i) => i !== index);
    setProfile({ ...profile, experience: newExperience });
  };

  const handleTechChange = (expIndex: number, value: string) => {
    const tech = value.split(',').map(s => s.trim()).filter(s => s);
    handleExperienceChange(expIndex, 'tech', tech);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(profile);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md space-y-6">
      <h2 className="text-2xl font-bold">Edit Profile</h2>

      {/* Basic Information */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Basic Information</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={profile.name}
            onChange={(e) => handleBasicInfoChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            value={profile.email}
            onChange={(e) => handleBasicInfoChange('email', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
          <textarea
            value={profile.summary || ''}
            onChange={(e) => handleBasicInfoChange('summary', e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Brief professional summary..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Links</label>
          {profile.links.map((link, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <input
                type="text"
                value={link}
                onChange={(e) => handleLinksChange(index, e.target.value)}
                placeholder="https://linkedin.com/in/..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={() => removeLink(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            onClick={addLink}
            className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            + Add Link
          </button>
        </div>
      </div>

      {/* Skills */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Skills</h3>
        {profile.skills.map((skillGroup, index) => (
          <div key={index} className="border p-4 rounded-md space-y-2">
            <div className="flex gap-2">
              <input
                type="text"
                value={skillGroup.category}
                onChange={(e) => handleSkillGroupChange(index, 'category', e.target.value)}
                placeholder="Category (e.g., Programming Languages)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={() => removeSkillGroup(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Remove
              </button>
            </div>
            <input
              type="text"
              value={skillGroup.skills.join(', ')}
              onChange={(e) => handleSkillsChange(index, e.target.value)}
              placeholder="Skills (comma-separated)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        ))}
        <button
          onClick={addSkillGroup}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          + Add Skill Group
        </button>
      </div>

      {/* Experience */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Experience</h3>
        {profile.experience.map((exp, expIndex) => (
          <div key={expIndex} className="border p-4 rounded-md space-y-3">
            <div className="flex justify-between items-start">
              <h4 className="font-semibold">Experience #{expIndex + 1}</h4>
              <button
                onClick={() => removeExperience(expIndex)}
                className="px-3 py-1 bg-red-500 text-white text-sm rounded-md hover:bg-red-600"
              >
                Remove
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                <input
                  type="text"
                  value={exp.company}
                  onChange={(e) => handleExperienceChange(expIndex, 'company', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={exp.title}
                  onChange={(e) => handleExperienceChange(expIndex, 'title', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dates</label>
              <input
                type="text"
                value={exp.dates}
                onChange={(e) => handleExperienceChange(expIndex, 'dates', e.target.value)}
                placeholder="e.g., Jan 2020 - Present"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Technologies (comma-separated)</label>
              <input
                type="text"
                value={exp.tech.join(', ')}
                onChange={(e) => handleTechChange(expIndex, e.target.value)}
                placeholder="Python, FastAPI, MongoDB"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Responsibilities</label>
              {exp.bullets.map((bullet, bulletIndex) => (
                <div key={bulletIndex} className="flex gap-2 mb-2">
                  <textarea
                    value={bullet.text}
                    onChange={(e) => handleBulletChange(expIndex, bulletIndex, e.target.value)}
                    rows={2}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Describe your achievement or responsibility..."
                  />
                  <button
                    onClick={() => removeBullet(expIndex, bulletIndex)}
                    className="px-3 py-2 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 self-start"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={() => addBullet(expIndex)}
                className="mt-2 px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded-md hover:bg-gray-300"
              >
                + Add Bullet
              </button>
            </div>
          </div>
        ))}
        <button
          onClick={addExperience}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          + Add Experience
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4 border-t">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
        >
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-semibold"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
