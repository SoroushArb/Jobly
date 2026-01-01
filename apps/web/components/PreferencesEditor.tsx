'use client';

import { useState, useEffect } from 'react';
import { Preferences } from '@/types/profile';

interface PreferencesEditorProps {
  initialPreferences: Preferences;
  onChange: (preferences: Preferences) => void;
}

const EUROPEAN_COUNTRIES = [
  'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
  'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary',
  'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
  'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
  'United Kingdom', 'Switzerland', 'Norway', 'Iceland'
];

const COMMON_LANGUAGES = [
  'English', 'German', 'French', 'Spanish', 'Italian', 'Dutch', 'Portuguese',
  'Polish', 'Swedish', 'Danish', 'Norwegian', 'Finnish', 'Greek', 'Czech'
];

export default function PreferencesEditor({ initialPreferences, onChange }: PreferencesEditorProps) {
  const [preferences, setPreferences] = useState<Preferences>(initialPreferences);

  useEffect(() => {
    setPreferences(initialPreferences);
  }, [initialPreferences]);

  const updatePreferences = (updates: Partial<Preferences>) => {
    const newPreferences = { ...preferences, ...updates };
    setPreferences(newPreferences);
    onChange(newPreferences);
  };

  const toggleCountry = (country: string) => {
    const countries = preferences.countries.includes(country)
      ? preferences.countries.filter(c => c !== country)
      : [...preferences.countries, country];
    updatePreferences({ countries });
  };

  const toggleLanguage = (language: string) => {
    const languages = preferences.languages.includes(language)
      ? preferences.languages.filter(l => l !== language)
      : [...preferences.languages, language];
    updatePreferences({ languages });
  };

  const handleCitiesChange = (value: string) => {
    const cities = value.split(',').map(c => c.trim()).filter(c => c);
    updatePreferences({ cities });
  };

  const handleSkillTagsChange = (value: string) => {
    const skill_tags = value.split(',').map(s => s.trim()).filter(s => s);
    updatePreferences({ skill_tags });
  };

  const handleRoleTagsChange = (value: string) => {
    const role_tags = value.split(',').map(r => r.trim()).filter(r => r);
    updatePreferences({ role_tags });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md space-y-6">
      <h2 className="text-2xl font-bold">Job Search Preferences</h2>

      {/* Location Preferences */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Location Preferences</h3>
        
        <div className="flex items-center space-x-6">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.europe}
              onChange={(e) => updatePreferences({ europe: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm font-medium">Open to Europe</span>
          </label>

          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.remote}
              onChange={(e) => updatePreferences({ remote: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm font-medium">Remote OK</span>
          </label>

          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.visa_required === true}
              onChange={(e) => updatePreferences({ visa_required: e.target.checked ? true : null })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm font-medium">Requires Visa Sponsorship</span>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Preferred Countries
          </label>
          <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto border p-3 rounded-md">
            {EUROPEAN_COUNTRIES.map(country => (
              <label key={country} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.countries.includes(country)}
                  onChange={() => toggleCountry(country)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm">{country}</span>
              </label>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Selected: {preferences.countries.length > 0 ? preferences.countries.join(', ') : 'None'}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Preferred Cities (comma-separated)
          </label>
          <input
            type="text"
            value={preferences.cities.join(', ')}
            onChange={(e) => handleCitiesChange(e.target.value)}
            placeholder="Berlin, Amsterdam, London"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Language Preferences */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Languages</h3>
        <div className="grid grid-cols-4 gap-2">
          {COMMON_LANGUAGES.map(language => (
            <label key={language} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.languages.includes(language)}
                onChange={() => toggleLanguage(language)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm">{language}</span>
            </label>
          ))}
        </div>
        <p className="text-xs text-gray-500">
          Selected: {preferences.languages.length > 0 ? preferences.languages.join(', ') : 'None'}
        </p>
      </div>

      {/* Skill and Role Preferences */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Skills & Roles</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Key Skill Tags (comma-separated)
          </label>
          <input
            type="text"
            value={preferences.skill_tags.join(', ')}
            onChange={(e) => handleSkillTagsChange(e.target.value)}
            placeholder="Python, FastAPI, React, AWS"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            Skills to prioritize in job searches
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Role Tags (comma-separated)
          </label>
          <input
            type="text"
            value={preferences.role_tags.join(', ')}
            onChange={(e) => handleRoleTagsChange(e.target.value)}
            placeholder="Backend Developer, Full-Stack Engineer, Software Engineer"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            Job titles to target
          </p>
        </div>
      </div>
    </div>
  );
}
