'use client';

import { useState, useEffect } from 'react';
import { CVDocument } from '@/types/profile';
import { listCVs, setActiveCV, deleteCV } from '@/lib/api';

interface CVSelectorProps {
  userEmail: string;
  onCVSelected?: (cv: CVDocument) => void;
}

export default function CVSelector({ userEmail, onCVSelected }: CVSelectorProps) {
  const [cvs, setCvs] = useState<CVDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchCVs = async () => {
    if (!userEmail) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await listCVs(userEmail);
      setCvs(response.cvs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load CVs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCVs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userEmail]);

  const handleSetActive = async (cvId: string) => {
    setError('');
    setSuccess('');
    
    if (!cvId) {
      setError('Invalid CV ID');
      return;
    }
    
    try {
      await setActiveCV(cvId, userEmail);
      setSuccess('CV set as active successfully!');
      
      // Refresh the list
      await fetchCVs();
      
      // Notify parent component
      const activeCv = cvs.find(cv => cv.id === cvId);
      if (activeCv && onCVSelected) {
        onCVSelected(activeCv);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set active CV');
    }
  };

  const handleDelete = async (cvId: string) => {
    if (!cvId) {
      setError('Invalid CV ID');
      return;
    }
    
    if (!confirm('Are you sure you want to delete this CV? This action cannot be undone.')) {
      return;
    }
    
    setError('');
    setSuccess('');
    
    try {
      await deleteCV(cvId, userEmail);
      setSuccess('CV deleted successfully!');
      
      // Refresh the list
      await fetchCVs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete CV');
    }
  };

  if (loading && cvs.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">Loading CVs...</p>
      </div>
    );
  }

  if (cvs.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">No CVs uploaded yet. Upload your first CV above.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Your CV Library</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <strong className="font-bold">Error: </strong>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          <strong className="font-bold">Success: </strong>
          <span>{success}</span>
        </div>
      )}

      <div className="space-y-3">
        {cvs.map((cv) => (
          <div
            key={cv.id}
            className={`border rounded-lg p-4 ${
              cv.is_active ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900">{cv.filename}</h3>
                  {cv.is_active && (
                    <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Uploaded: {new Date(cv.upload_date).toLocaleDateString()} at{' '}
                  {new Date(cv.upload_date).toLocaleTimeString()}
                </p>
                <p className="text-sm text-gray-600">
                  Profile: {cv.parsed_profile.name} ({cv.parsed_profile.email})
                </p>
              </div>

              <div className="flex gap-2">
                {!cv.is_active && cv.id && (
                  <button
                    onClick={() => handleSetActive(cv.id!)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                  >
                    Set Active
                  </button>
                )}
                {cv.id && (
                  <button
                    onClick={() => handleDelete(cv.id!)}
                    className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-4 text-sm text-gray-600">
        Total CVs: {cvs.length} | Active CV will be used for job matching and applications
      </p>
    </div>
  );
}
