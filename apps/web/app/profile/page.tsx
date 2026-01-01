'use client';

import { useState } from 'react';
import CVUpload from '@/components/CVUpload';
import ExtractedTextPreview from '@/components/ExtractedTextPreview';
import ProfileEditor from '@/components/ProfileEditor';
import PreferencesEditor from '@/components/PreferencesEditor';
import { UserProfile } from '@/types/profile';
import { saveProfile } from '@/lib/api';

export default function ProfilePage() {
  const [extractedText, setExtractedText] = useState<string>('');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences'>('profile');

  const handleUploadSuccess = (text: string, draftProfile: UserProfile) => {
    setExtractedText(text);
    setProfile(draftProfile);
    setError('');
    setSuccess('CV uploaded and parsed successfully!');
  };

  const handleUploadError = (errorMsg: string) => {
    setError(errorMsg);
    setSuccess('');
  };

  const handleSaveProfile = async (updatedProfile: UserProfile) => {
    try {
      setError('');
      const response = await saveProfile(updatedProfile);
      setSuccess(`Profile saved successfully! ID: ${response.profile_id}`);
      setProfile(updatedProfile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
      throw err;
    }
  };

  const handlePreferencesChange = (updatedPreferences: any) => {
    if (profile) {
      setProfile({ ...profile, preferences: updatedPreferences });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Profile Management</h1>
          <p className="mt-2 text-lg text-gray-600">
            Upload your CV and manage your job search profile
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

        {/* Upload Section */}
        {!profile && (
          <div className="mb-8">
            <CVUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
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
          <div className="space-y-6">
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
                        onClick={() => handleSaveProfile(profile)}
                        className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-semibold"
                      >
                        Save Preferences
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
