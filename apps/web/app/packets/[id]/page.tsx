'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Packet } from '@/types/packet';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PacketDetailPage() {
  const params = useParams();
  const packetId = params.id as string;
  
  const [packet, setPacket] = useState<Packet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!packetId) return;

    const fetchPacket = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_URL}/packets/${packetId}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch packet');
        }

        const data = await response.json();
        setPacket(data.packet);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch packet');
      } finally {
        setLoading(false);
      }
    };

    fetchPacket();
  }, [packetId]);

  const downloadFile = (fileType: string, filename: string) => {
    window.open(`${API_URL}/packets/${packetId}/download/${fileType}`, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading packet...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !packet) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-semibold mb-2">Error</h2>
            <p className="text-red-600">{error || 'Packet not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Application Packet</h1>
          <p className="text-gray-600">
            Created: {new Date(packet.created_at).toLocaleString()}
          </p>
        </div>

        {/* Tailored Summary */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Tailored Summary</h2>
          <p className="text-gray-700 mb-4">{packet.tailoring_plan.summary_rewrite}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {/* Priority Skills */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Priority Skills</h3>
              <div className="flex flex-wrap gap-2">
                {packet.tailoring_plan.skills_priority.slice(0, 10).map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-block bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Gaps */}
            {packet.tailoring_plan.gaps.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Skill Gaps</h3>
                <div className="flex flex-wrap gap-2">
                  {packet.tailoring_plan.gaps.slice(0, 5).map((gap, idx) => (
                    <span
                      key={idx}
                      className="inline-block bg-yellow-50 text-yellow-700 px-3 py-1 rounded-full text-sm"
                    >
                      {gap}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Download Links */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Download Files</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* CV LaTeX */}
            <button
              onClick={() => downloadFile('tex', packet.cv_tex.filename)}
              className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
            >
              <div className="flex items-center">
                <svg className="w-8 h-8 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div className="text-left">
                  <p className="font-medium text-gray-900">CV (LaTeX)</p>
                  <p className="text-sm text-gray-500">{packet.cv_tex.filename}</p>
                </div>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>

            {/* CV PDF */}
            {packet.cv_pdf && (
              <button
                onClick={() => downloadFile('pdf', packet.cv_pdf!.filename)}
                className="flex items-center justify-between p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors"
              >
                <div className="flex items-center">
                  <svg className="w-8 h-8 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">CV (PDF)</p>
                    <p className="text-sm text-gray-500">{packet.cv_pdf.filename}</p>
                  </div>
                </div>
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
            )}

            {/* Cover Letter */}
            {packet.cover_letter && (
              <button
                onClick={() => downloadFile('cover_letter', packet.cover_letter!.filename)}
                className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
              >
                <div className="flex items-center">
                  <svg className="w-8 h-8 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Cover Letter</p>
                    <p className="text-sm text-gray-500">{packet.cover_letter.filename}</p>
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
            )}

            {/* Recruiter Message */}
            <button
              onClick={() => downloadFile('recruiter_message', packet.recruiter_message.filename)}
              className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
            >
              <div className="flex items-center">
                <svg className="w-8 h-8 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Recruiter Message</p>
                  <p className="text-sm text-gray-500">{packet.recruiter_message.filename}</p>
                </div>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>

            {/* Common Answers */}
            <button
              onClick={() => downloadFile('common_answers', packet.common_answers.filename)}
              className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
            >
              <div className="flex items-center">
                <svg className="w-8 h-8 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Common Answers</p>
                  <p className="text-sm text-gray-500">{packet.common_answers.filename}</p>
                </div>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Integrity Notes */}
        {packet.tailoring_plan.integrity_notes.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-yellow-900 mb-3">⚠️ Integrity Notes</h2>
            <ul className="list-disc list-inside space-y-1 text-yellow-800">
              {packet.tailoring_plan.integrity_notes.map((note, idx) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Bullet Suggestions */}
        {packet.tailoring_plan.bullet_swaps.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Suggested Improvements</h2>
            <div className="space-y-4">
              {packet.tailoring_plan.bullet_swaps.map((swap, idx) => (
                <div key={idx} className="border-l-4 border-blue-400 pl-4 py-2">
                  <p className="text-sm text-gray-600 mb-1">Role #{swap.role_index + 1}</p>
                  <p className="text-gray-700 mb-2">{swap.suggested_bullet}</p>
                  <p className="text-sm text-blue-600 italic">{swap.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
