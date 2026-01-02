'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getInterviewMaterials } from '@/lib/api';
import { InterviewPack, TechnicalQA, STARStory, TechnicalQATopic } from '@/types/interview';

export default function InterviewPage() {
  const params = useParams();
  const router = useRouter();
  const packetId = params.packet_id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [interviewPack, setInterviewPack] = useState<InterviewPack | null>(null);
  const [technicalQA, setTechnicalQA] = useState<TechnicalQA | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  useEffect(() => {
    async function fetchInterviewMaterials() {
      try {
        setLoading(true);
        const response = await getInterviewMaterials(packetId);
        setInterviewPack(response.interview_pack);
        setTechnicalQA(response.technical_qa);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load interview materials');
      } finally {
        setLoading(false);
      }
    }

    fetchInterviewMaterials();
  }, [packetId]);

  const exportToMarkdown = () => {
    if (!interviewPack || !technicalQA) return;

    let markdown = `# Interview Preparation Pack\n\n`;
    markdown += `**Company:** ${interviewPack.company_name}\n`;
    markdown += `**Role:** ${interviewPack.role_title}\n`;
    markdown += `**Generated:** ${new Date(interviewPack.generated_at).toLocaleString()}\n\n`;

    markdown += `---\n\n## Role Overview\n\n${interviewPack.role_digest}\n\n`;
    markdown += `## Company Information\n\n${interviewPack.company_digest}\n\n`;

    if (interviewPack.integrity_note) {
      markdown += `> ⚠️ **Note:** ${interviewPack.integrity_note}\n\n`;
    }

    markdown += `---\n\n## 30/60/90 Day Plan\n\n`;
    markdown += `### First 30 Days\n\n${interviewPack.plan_30_days.map(item => `- ${item}`).join('\n')}\n\n`;
    markdown += `### First 60 Days\n\n${interviewPack.plan_60_days.map(item => `- ${item}`).join('\n')}\n\n`;
    markdown += `### First 90 Days\n\n${interviewPack.plan_90_days.map(item => `- ${item}`).join('\n')}\n\n`;

    markdown += `---\n\n## STAR Stories\n\n`;
    interviewPack.star_stories.forEach((story, idx) => {
      markdown += `### ${idx + 1}. ${story.title}\n\n`;
      markdown += `**Skills Demonstrated:** ${story.skills_demonstrated.join(', ')}\n\n`;
      markdown += `**Situation:** ${story.situation}\n\n`;
      markdown += `**Task:** ${story.task}\n\n`;
      markdown += `**Action:** ${story.action}\n\n`;
      markdown += `**Result:** ${story.result}\n\n`;
      if (story.grounding_refs.length > 0) {
        markdown += `*Grounded in experience: ${story.grounding_refs.map(r => r.evidence_text).join('; ')}*\n\n`;
      }
    });

    markdown += `---\n\n## Questions to Ask\n\n`;
    const questionsByCategory: { [key: string]: typeof interviewPack.questions_to_ask } = {};
    interviewPack.questions_to_ask.forEach(q => {
      if (!questionsByCategory[q.category]) {
        questionsByCategory[q.category] = [];
      }
      questionsByCategory[q.category].push(q);
    });
    Object.entries(questionsByCategory).forEach(([category, questions]) => {
      markdown += `### ${category.charAt(0).toUpperCase() + category.slice(1)}\n\n`;
      questions.forEach(q => {
        markdown += `- ${q.question}\n  *${q.reasoning}*\n\n`;
      });
    });

    markdown += `---\n\n## Study Checklist\n\n`;
    interviewPack.study_checklist.forEach(resource => {
      markdown += `- **${resource.topic}** (${resource.resource_type}): ${resource.description}\n`;
    });

    markdown += `\n---\n\n## Technical Q&A\n\n`;
    markdown += `**Priority Topics:** ${technicalQA.priority_topics.join(', ')}\n\n`;

    technicalQA.topics.forEach(topic => {
      markdown += `### ${topic.topic}\n\n`;
      topic.questions.forEach((q, idx) => {
        markdown += `#### Question ${idx + 1} [${q.difficulty.toUpperCase()}]\n\n`;
        markdown += `**Q:** ${q.question}\n\n`;
        markdown += `**A:** ${q.answer}\n\n`;
        if (q.follow_ups.length > 0) {
          markdown += `**Follow-ups:**\n${q.follow_ups.map(f => `- ${f}`).join('\n')}\n\n`;
        }
        markdown += `**Key Concepts:** ${q.key_concepts.join(', ')}\n\n`;
      });
    });

    // Create download
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-prep-${interviewPack.company_name.replace(/\s+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">Loading interview materials...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-900 mb-2">Error Loading Materials</h2>
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => router.back()}
              className="mt-4 px-4 py-2 bg-red-100 text-red-900 rounded hover:bg-red-200"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!interviewPack || !technicalQA) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">No interview materials found.</div>
        </div>
      </div>
    );
  }

  // Filter technical questions
  const filteredTopics = technicalQA.topics.map(topic => ({
    ...topic,
    questions: topic.questions.filter(q => {
      const matchesSearch = searchQuery === '' ||
        q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.key_concepts.some(c => c.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesDifficulty = selectedDifficulty === 'all' || q.difficulty === selectedDifficulty;
      return matchesSearch && matchesDifficulty;
    })
  })).filter(topic => topic.questions.length > 0);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Preparation</h1>
              <p className="text-xl text-gray-700">{interviewPack.role_title} at {interviewPack.company_name}</p>
              <p className="text-sm text-gray-500 mt-2">
                Generated: {new Date(interviewPack.generated_at).toLocaleString()}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={exportToMarkdown}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Export to Markdown
              </button>
              <button
                onClick={() => router.back()}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Back
              </button>
            </div>
          </div>
          
          {interviewPack.integrity_note && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
              <p className="text-sm text-yellow-900">
                <strong>⚠️ Note:</strong> {interviewPack.integrity_note}
              </p>
            </div>
          )}
        </div>

        {/* Role & Company Digest */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Role Overview</h2>
          <p className="text-gray-700 mb-6">{interviewPack.role_digest}</p>
          
          <h3 className="text-xl font-bold text-gray-900 mb-2">Company Information</h3>
          <p className="text-gray-700">{interviewPack.company_digest}</p>
        </div>

        {/* 30/60/90 Plan */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">30/60/90 Day Plan</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-3">First 30 Days</h3>
              <ul className="space-y-2">
                {interviewPack.plan_30_days.map((item, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-green-900 mb-3">First 60 Days</h3>
              <ul className="space-y-2">
                {interviewPack.plan_60_days.map((item, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-green-600 mr-2">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-purple-900 mb-3">First 90 Days</h3>
              <ul className="space-y-2">
                {interviewPack.plan_90_days.map((item, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* STAR Stories */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">STAR Stories</h2>
          <p className="text-sm text-gray-600 mb-4">
            Use these stories to answer behavioral interview questions. All stories are grounded in your real experience.
          </p>
          
          <div className="space-y-6">
            {interviewPack.star_stories.map((story, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{story.title}</h3>
                  <div className="flex flex-wrap gap-1">
                    {story.skills_demonstrated.map((skill, sidx) => (
                      <span key={sidx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <strong className="text-sm text-gray-700">Situation:</strong>
                    <p className="text-gray-600 mt-1">{story.situation}</p>
                  </div>
                  <div>
                    <strong className="text-sm text-gray-700">Task:</strong>
                    <p className="text-gray-600 mt-1">{story.task}</p>
                  </div>
                  <div>
                    <strong className="text-sm text-gray-700">Action:</strong>
                    <p className="text-gray-600 mt-1">{story.action}</p>
                  </div>
                  <div>
                    <strong className="text-sm text-gray-700">Result:</strong>
                    <p className="text-gray-600 mt-1">{story.result}</p>
                  </div>
                </div>
                
                {story.grounding_refs.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      <strong>Grounded in:</strong> {story.grounding_refs.map(ref => ref.evidence_text).join('; ')}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Questions to Ask */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Questions to Ask Interviewer</h2>
          
          <div className="space-y-4">
            {interviewPack.questions_to_ask.map((question, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="text-gray-900 font-medium">{question.question}</p>
                <p className="text-sm text-gray-600 mt-1">
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs mr-2">
                    {question.category}
                  </span>
                  {question.reasoning}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Study Checklist */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Study Checklist</h2>
          <p className="text-sm text-gray-600 mb-4">
            Topics to review based on job requirements and identified gaps. Add your own resources.
          </p>
          
          <div className="space-y-3">
            {interviewPack.study_checklist.map((resource, idx) => (
              <div key={idx} className="flex items-start">
                <input type="checkbox" className="mt-1 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">
                    {resource.topic}
                    <span className="ml-2 text-xs text-gray-500">({resource.resource_type})</span>
                  </p>
                  <p className="text-sm text-gray-600">{resource.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Q&A */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Technical Q&A</h2>
              <p className="text-sm text-gray-600 mt-1">
                Priority topics: {technicalQA.priority_topics.join(', ')}
              </p>
            </div>
          </div>
          
          {/* Search and Filter */}
          <div className="flex gap-4 mb-6">
            <input
              type="text"
              placeholder="Search questions, answers, or concepts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          
          {/* Topics */}
          <div className="space-y-6">
            {filteredTopics.map((topic, tidx) => (
              <div key={tidx}>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{topic.topic}</h3>
                
                <div className="space-y-4">
                  {topic.questions.map((question, qidx) => (
                    <div key={qidx} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-gray-900">{question.question}</h4>
                        <span className={`px-2 py-1 text-xs rounded ${
                          question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                          question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {question.difficulty.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="mt-3">
                        <p className="text-gray-700 whitespace-pre-wrap">{question.answer}</p>
                      </div>
                      
                      {question.follow_ups.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-sm font-medium text-gray-700 mb-2">Follow-up questions:</p>
                          <ul className="space-y-1">
                            {question.follow_ups.map((followUp, fidx) => (
                              <li key={fidx} className="text-sm text-gray-600 flex items-start">
                                <span className="mr-2">→</span>
                                {followUp}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-500">
                          <strong>Key concepts:</strong> {question.key_concepts.join(', ')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          {filteredTopics.length === 0 && (
            <p className="text-center text-gray-500 py-8">
              No questions match your search criteria.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
