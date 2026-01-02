'use client';

import { useState, useEffect } from 'react';
import CVUpload from '@/components/CVUpload';
import CVSelector from '@/components/CVSelector';
import ExtractedTextPreview from '@/components/ExtractedTextPreview';
import ProfileEditor from '@/components/ProfileEditor';
import PreferencesEditor from '@/components/PreferencesEditor';
import { UserProfile } from '@/types/profile';
import { saveProfile, savePreferences } from '@/lib/api';

export default function ProfilePage() {
  const [extractedText, setExtractedText] = useState<string>('');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences'>('profile');
  const [savingPreferences, setSavingPreferences] = useState(false);

  const handleUploadSuccess = (text: string, draftProfile: UserProfile) => {
    setExtractedText(text);
    setProfile(draftProfile);
    setError('');
    setSuccess('CV uploaded and parsed successfully! Review your profile below.');
    
    // Auto-scroll to profile section
    setTimeout(() => {
      const profileSection = document.getElementById('profile-section');
      if (profileSection) {
        profileSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const handleUploadError = (errorMsg: string) => {
    setError(errorMsg);
    setSuccess('');
  };

  const handleSaveProfile = async (updatedProfile: UserProfile) => {
    try {
      setError('');
      setSuccess('');
      const response = await saveProfile(updatedProfile);
      setSuccess(`Profile saved successfully! ${response.message}`);
      setProfile(updatedProfile);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to save profile';
      setError(errorMsg);
      throw err;
    }
  };

  const handlePreferencesChange = (updatedPreferences: any) => {
    if (profile) {
      setProfile({ ...profile, preferences: updatedPreferences });
    }
  };

  const handleSavePreferences = async () => {
    if (!profile) return;
    
    setSavingPreferences(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await savePreferences(profile.email, profile.preferences);
      setSuccess(`Preferences saved successfully! ${response.message}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to save preferences';
      setError(errorMsg);
    } finally {
      setSavingPreferences(false);
    }
  };

  const handleCVSelected = (cv: any) => {
    // When a CV is set as active, load its profile
    if (cv && cv.parsed_profile) {
      setProfile(cv.parsed_profile);
      setSuccess('Active CV profile loaded!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Profile Management</h1>
          <p className="mt-2 text-lg text-gray-600">
            Upload your CV, manage multiple profiles, and configure job search preferences
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            <strong className="font-bold">Error: </strong>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            <strong className="font-bold">Success: </strong>
            <span>{success}</span>
          </div>
        )}

        {/* Upload Section - Always visible */}
        <div className="mb-8">
          <CVUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>

        {/* CV Library - Show if profile exists (meaning at least one CV was uploaded) */}
        {profile && (
          <div className="mb-8">
            <CVSelector
              userEmail={profile.email}
              onCVSelected={handleCVSelected}
            />
          </div>
        )}

        {/* Extracted Text Preview */}
        {extractedText && (
          <div className="mb-8">
            <ExtractedTextPreview text={extractedText} />
          </div>
        )}

        {/* Profile Editor */}
        {profile && (
          <div id="profile-section" className="space-y-6">
            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px">
                  <button
                    onClick={() => setActiveTab('profile')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 ${
                      activeTab === 'profile'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Profile Information
                  </button>
                  <button
                    onClick={() => setActiveTab('preferences')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 ${
                      activeTab === 'preferences'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Job Preferences
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'profile' ? (
                  <ProfileEditor
                    initialProfile={profile}
                    onSave={handleSaveProfile}
                    onCancel={() => {
                      setProfile(null);
                      setExtractedText('');
                    }}
                  />
                ) : (
                  <div>
                    <PreferencesEditor
                      initialPreferences={profile.preferences}
                      onChange={handlePreferencesChange}
                    />
                    <div className="mt-6 flex justify-end">
                      <button
                        onClick={handleSavePreferences}
                        disabled={savingPreferences}
                        className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
                      >
                        {savingPreferences ? 'Saving...' : 'Save Preferences'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
