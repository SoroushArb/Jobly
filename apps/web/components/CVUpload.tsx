'use client';

import { useState } from 'react';

interface CVUploadProps {
  onUploadSuccess: (extractedText: string, profile: any) => void;
  onUploadError: (error: string) => void;
}

export default function CVUpload({ onUploadSuccess, onUploadError }: CVUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      onUploadError('Please select a file');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/profile/upload-cv`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload CV');
      }

      const data = await response.json();
      onUploadSuccess(data.extracted_text, data.draft_profile);
    } catch (error) {
      onUploadError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Upload Your CV</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select PDF or DOCX file
          </label>
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>
        {file && (
          <p className="text-sm text-gray-600">
            Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </p>
        )}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Upload & Parse CV'}
        </button>
      </div>
    </div>
  );
}
