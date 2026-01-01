'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MatchWithJob, RecomputeMatchesResponse } from '@/types/match';
import { GeneratePacketRequest } from '@/types/packet';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function MatchesPage() {
  const router = useRouter();
  const [matches, setMatches] = useState<MatchWithJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);
  const [generatingPacket, setGeneratingPacket] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<MatchWithJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [minScore, setMinScore] = useState<string>('');
  const [remote, setRemote] = useState<boolean | null>(null);
  const [country, setCountry] = useState('');
  const [city, setCity] = useState('');

  const fetchMatches = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (minScore) params.append('min_score', minScore);
      if (remote !== null) params.append('remote', String(remote));
      if (country) params.append('country', country);
      if (city) params.append('city', city);
      
      const response = await fetch(`${API_URL}/matches?${params.toString()}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch matches');
      }
      
      const data = await response.json();
      setMatches(data.matches || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const recomputeMatches = async () => {
    try {
      setComputing(true);
      setError(null);
      
      const response = await fetch(`${API_URL}/matches/recompute`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to recompute matches');
      }
      
      const data: RecomputeMatchesResponse = await response.json();
      alert(`Successfully computed ${data.matches_computed} matches!`);
      
      // Refresh matches
      await fetchMatches();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to recompute matches');
    } finally {
      setComputing(false);
    }
  };

  const generatePacket = async (jobId: string, includeCoverLetter: boolean = false) => {
    try {
      setGeneratingPacket(true);
      setError(null);

      const request: GeneratePacketRequest = {
        job_id: jobId,
        include_cover_letter: includeCoverLetter,
      };

      const response = await fetch(`${API_URL}/packets/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate packet');
      }

      const data = await response.json();
      
      // Close modal
      setSelectedMatch(null);
      
      // Navigate to packet page
      router.push(`/packets/${data.packet.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate packet');
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to generate packet'}`);
    } finally {
      setGeneratingPacket(false);
    }
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  const handleApplyFilters = () => {
    fetchMatches();
  };

  const handleClearFilters = () => {
    setMinScore('');
    setRemote(null);
    setCountry('');
    setCity('');
    setTimeout(() => fetchMatches(), 100);
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 font-semibold';
    if (score >= 0.5) return 'text-yellow-600 font-semibold';
    return 'text-gray-600';
  };

  const getRemoteBadgeColor = (remoteType: string) => {
    switch (remoteType) {
      case 'remote':
        return 'bg-green-100 text-green-800';
      case 'hybrid':
        return 'bg-blue-100 text-blue-800';
      case 'onsite':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Matches</h1>
          <p className="text-gray-600">AI-powered job recommendations based on your profile</p>
        </div>

        {/* Actions */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={recomputeMatches}
            disabled={computing}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {computing ? 'Computing...' : 'Recompute Matches'}
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Score (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={minScore}
                onChange={(e) => setMinScore(e.target.value)}
                placeholder="e.g., 50"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Remote Type
              </label>
              <select
                value={remote === null ? '' : String(remote)}
                onChange={(e) => setRemote(e.target.value === '' ? null : e.target.value === 'true')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">All</option>
                <option value="true">Remote Only</option>
                <option value="false">Not Remote</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <input
                type="text"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                placeholder="e.g., Germany"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="e.g., Berlin"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={handleApplyFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Apply Filters
            </button>
            <button
              onClick={handleClearFilters}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
            {error.includes('No profile found') && (
              <p className="text-sm text-red-600 mt-2">
                Please create a profile first by visiting the{' '}
                <a href="/profile" className="underline">Profile page</a>.
              </p>
            )}
            {error.includes('No jobs found') && (
              <p className="text-sm text-red-600 mt-2">
                Please run job ingestion first by visiting the{' '}
                <a href="/jobs" className="underline">Jobs page</a>.
              </p>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading matches...</p>
          </div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600">No matches found.</p>
            <p className="text-sm text-gray-500 mt-2">
              Try adjusting your filters or click &quot;Recompute Matches&quot; to generate new matches.
            </p>
          </div>
        ) : (
          <>
            {/* Matches Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Job Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Remote
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Top Reasons
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {matches.map((matchWithJob) => (
                    <tr key={matchWithJob.match.job_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-lg ${getScoreColor(matchWithJob.match.score_total)}`}>
                          {formatScore(matchWithJob.match.score_total)}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {matchWithJob.job.title}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{matchWithJob.job.company}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {matchWithJob.job.city && `${matchWithJob.job.city}, `}
                          {matchWithJob.job.country}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${getRemoteBadgeColor(matchWithJob.job.remote_type)}`}>
                          {matchWithJob.job.remote_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <ul className="text-sm text-gray-600 space-y-1">
                          {matchWithJob.match.top_reasons.slice(0, 2).map((reason, idx) => (
                            <li key={idx}>• {reason}</li>
                          ))}
                        </ul>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => setSelectedMatch(matchWithJob)}
                          className="text-blue-600 hover:text-blue-800 mr-3"
                        >
                          View Details
                        </button>
                        <button
                          onClick={() => generatePacket(matchWithJob.job._id || '', false)}
                          disabled={generatingPacket}
                          className="text-purple-600 hover:text-purple-800 mr-3 disabled:text-gray-400"
                        >
                          Generate Packet
                        </button>
                        <a
                          href={matchWithJob.job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-green-600 hover:text-green-800"
                        >
                          Apply →
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 text-sm text-gray-600">
              Showing {matches.length} match{matches.length !== 1 ? 'es' : ''}
            </div>
          </>
        )}

        {/* Match Detail Modal */}
        {selectedMatch && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {selectedMatch.job.title}
                    </h2>
                    <p className="text-lg text-gray-600">{selectedMatch.job.company}</p>
                  </div>
                  <button
                    onClick={() => setSelectedMatch(null)}
                    className="text-gray-400 hover:text-gray-600 text-2xl"
                  >
                    ×
                  </button>
                </div>

                {/* Match Score */}
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Match Score</span>
                    <span className={`text-3xl ${getScoreColor(selectedMatch.match.score_total)}`}>
                      {formatScore(selectedMatch.match.score_total)}%
                    </span>
                  </div>
                  
                  {/* Score Breakdown */}
                  <div className="mt-4 space-y-2">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Score Breakdown</h3>
                    {Object.entries(selectedMatch.match.score_breakdown).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-600"
                              style={{ width: `${value * 100}%` }}
                            />
                          </div>
                          <span className="text-gray-900 w-12 text-right">
                            {formatScore(value)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Reasons */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Why This Match?</h3>
                  <ul className="space-y-2">
                    {selectedMatch.match.top_reasons.map((reason, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-green-600 mr-2">✓</span>
                        <span className="text-gray-700">{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Gaps */}
                {selectedMatch.match.gaps.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Potential Gaps</h3>
                    <ul className="space-y-2">
                      {selectedMatch.match.gaps.map((gap, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-yellow-600 mr-2">!</span>
                          <span className="text-gray-700">{gap}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {selectedMatch.match.recommendations.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommendations</h3>
                    <ul className="space-y-2">
                      {selectedMatch.match.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-blue-600 mr-2">→</span>
                          <span className="text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Job Details */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Job Details</h3>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Location</span>
                      <p className="text-gray-900">
                        {selectedMatch.job.city && `${selectedMatch.job.city}, `}
                        {selectedMatch.job.country}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Remote Type</span>
                      <p className="text-gray-900 capitalize">{selectedMatch.job.remote_type}</p>
                    </div>
                    {selectedMatch.job.employment_type && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Employment Type</span>
                        <p className="text-gray-900 capitalize">{selectedMatch.job.employment_type}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 flex gap-3">
                  <a
                    href={selectedMatch.job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-center"
                  >
                    Apply for This Job →
                  </a>
                  <button
                    onClick={() => generatePacket(selectedMatch.job._id || '', false)}
                    disabled={generatingPacket}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {generatingPacket ? 'Generating...' : 'Generate Application Packet'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
