'use client';

import { useState, useEffect } from 'react';
import { JobPostingInDB, JobFilters } from '@/types/job';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPostingInDB[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedJob, setSelectedJob] = useState<JobPostingInDB | null>(null);
  const [isIngesting, setIsIngesting] = useState(false);

  // Filters
  const [filters, setFilters] = useState<JobFilters>({
    remote_type: '',
    country: '',
    city: '',
    keyword: '',
    title: '',
    page: 1,
    per_page: 50
  });

  // Fetch jobs
  const fetchJobs = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Build query params
      const params = new URLSearchParams();
      if (filters.remote_type) params.append('remote_type', filters.remote_type);
      if (filters.country) params.append('country', filters.country);
      if (filters.city) params.append('city', filters.city);
      if (filters.title) params.append('title', filters.title);
      if (filters.keyword) params.append('keyword', filters.keyword);
      params.append('page', filters.page?.toString() || '1');
      params.append('per_page', filters.per_page?.toString() || '50');

      const response = await fetch(`${apiUrl}/jobs?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }

      const data = await response.json();
      setJobs(data.jobs);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  // Trigger ingestion
  const triggerIngestion = async () => {
    setIsIngesting(true);
    setError('');
    
    try {
      const response = await fetch(`${apiUrl}/jobs/ingest`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Ingestion failed');
      }

      const data = await response.json();
      alert(`Ingestion completed!\n${data.jobs_new} new jobs, ${data.jobs_updated} updated jobs`);
      
      // Refresh job list
      fetchJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed');
    } finally {
      setIsIngesting(false);
    }
  };

  // Load jobs on mount and when pagination changes
  useEffect(() => {
    fetchJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.page, filters.per_page]);

  // Handle filter change
  const handleFilterChange = (key: keyof JobFilters, value: string | number) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 })); // Reset to page 1
  };

  // Apply filters button
  const applyFilters = () => {
    fetchJobs();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Job Listings</h1>
          <p className="mt-2 text-gray-600">
            Browse and filter job postings from configured sources
          </p>
        </div>

        {/* Ingest Button */}
        <div className="mb-6">
          <button
            onClick={triggerIngestion}
            disabled={isIngesting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isIngesting ? 'Ingesting...' : 'Trigger Job Ingestion'}
          </button>
          <span className="ml-4 text-sm text-gray-600">
            Fetch latest jobs from all configured sources
          </span>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-lg font-semibold mb-4">Search & Filter Jobs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Job Title (Specific Search) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title
              </label>
              <input
                type="text"
                value={filters.title || ''}
                onChange={(e) => handleFilterChange('title', e.target.value)}
                placeholder="e.g., Software Engineer"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Search in job titles specifically</p>
            </div>

            {/* Remote Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Remote Type
              </label>
              <select
                value={filters.remote_type}
                onChange={(e) => handleFilterChange('remote_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">Onsite</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <input
                type="text"
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                placeholder="e.g., Germany"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* City */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={filters.city}
                onChange={(e) => handleFilterChange('city', e.target.value)}
                placeholder="e.g., Berlin"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* General Keyword Search */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keyword Search (searches in title, company, description)
            </label>
            <input
              type="text"
              value={filters.keyword}
              onChange={(e) => handleFilterChange('keyword', e.target.value)}
              placeholder="Search across all fields..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="mt-4 flex gap-2">
            <button
              onClick={applyFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-semibold"
            >
              Apply Filters
            </button>
            <button
              onClick={() => {
                setFilters({ remote_type: '', country: '', city: '', keyword: '', title: '', page: 1, per_page: 50 });
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Job Count */}
        <div className="mb-4">
          <p className="text-gray-600">
            {loading ? 'Loading...' : `Showing ${jobs.length} of ${total} jobs`}
          </p>
        </div>

        {/* Jobs Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
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
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {jobs.length === 0 && !loading && (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      No jobs found. Try adjusting your filters or trigger job ingestion.
                    </td>
                  </tr>
                )}
                {jobs.map((job) => (
                  <tr key={job._id || job.dedupe_hash} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{job.title}</div>
                      {job.employment_type && (
                        <div className="text-xs text-gray-500">{job.employment_type}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{job.company}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {job.city && job.country ? `${job.city}, ${job.country}` : job.location || 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        job.remote_type === 'remote' ? 'bg-green-100 text-green-800' :
                        job.remote_type === 'hybrid' ? 'bg-blue-100 text-blue-800' :
                        job.remote_type === 'onsite' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {job.remote_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{job.source_name}</td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => setSelectedJob(job)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        View
                      </button>
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Apply →
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        {total > (filters.per_page || 50) && (
          <div className="mt-6 flex justify-center space-x-2">
            <button
              onClick={() => handleFilterChange('page', (filters.page || 1) - 1)}
              disabled={filters.page === 1}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-gray-700">
              Page {filters.page} of {Math.ceil(total / (filters.per_page || 50))}
            </span>
            <button
              onClick={() => handleFilterChange('page', (filters.page || 1) + 1)}
              disabled={(filters.page || 1) >= Math.ceil(total / (filters.per_page || 50))}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Job Detail Modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedJob.title}</h2>
                  <p className="text-lg text-gray-600">{selectedJob.company}</p>
                </div>
                <button
                  onClick={() => setSelectedJob(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                {/* Location */}
                <div>
                  <h3 className="font-semibold text-gray-700">Location</h3>
                  <p className="text-gray-600">
                    {selectedJob.city && selectedJob.country 
                      ? `${selectedJob.city}, ${selectedJob.country}` 
                      : selectedJob.location || 'N/A'}
                  </p>
                </div>

                {/* Remote Type */}
                <div>
                  <h3 className="font-semibold text-gray-700">Remote Type</h3>
                  <span className={`inline-block px-3 py-1 text-sm rounded-full ${
                    selectedJob.remote_type === 'remote' ? 'bg-green-100 text-green-800' :
                    selectedJob.remote_type === 'hybrid' ? 'bg-blue-100 text-blue-800' :
                    selectedJob.remote_type === 'onsite' ? 'bg-gray-100 text-gray-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {selectedJob.remote_type}
                  </span>
                </div>

                {/* Employment Type */}
                {selectedJob.employment_type && (
                  <div>
                    <h3 className="font-semibold text-gray-700">Employment Type</h3>
                    <p className="text-gray-600">{selectedJob.employment_type}</p>
                  </div>
                )}

                {/* Description */}
                {selectedJob.description_clean && (
                  <div>
                    <h3 className="font-semibold text-gray-700">Description</h3>
                    <div className="text-gray-600 whitespace-pre-wrap">
                      {selectedJob.description_clean}
                    </div>
                  </div>
                )}

                {/* Source Info */}
                <div>
                  <h3 className="font-semibold text-gray-700">Source</h3>
                  <p className="text-gray-600">{selectedJob.source_name}</p>
                  {selectedJob.source_compliance_note && (
                    <p className="text-xs text-gray-500 mt-1">{selectedJob.source_compliance_note}</p>
                  )}
                </div>

                {/* Dates */}
                <div className="text-sm text-gray-500">
                  <p>First seen: {new Date(selectedJob.first_seen).toLocaleDateString()}</p>
                  <p>Last seen: {new Date(selectedJob.last_seen).toLocaleDateString()}</p>
                </div>

                {/* Apply Button */}
                <div className="pt-4">
                  <a
                    href={selectedJob.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Apply on {selectedJob.source_name} →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
