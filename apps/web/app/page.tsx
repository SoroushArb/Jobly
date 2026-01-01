import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Jobly
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              AI-Powered Job Hunter Agent - Phase 1
            </p>
            <p className="text-lg text-gray-700 max-w-2xl mx-auto">
              Upload your CV, create your profile, and set your job search preferences 
              to get started with intelligent job hunting.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                📄 Profile Management
              </h2>
              <p className="text-gray-600 mb-6">
                Upload your CV (PDF or DOCX) and we&apos;ll automatically extract your 
                information into a structured profile that you can edit and refine.
              </p>
              <Link
                href="/profile"
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 font-semibold"
              >
                Manage Profile
              </Link>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                🎯 Job Preferences
              </h2>
              <p className="text-gray-600 mb-6">
                Set your location preferences, target roles, desired skills, 
                and language requirements to help us find the perfect jobs for you.
              </p>
              <Link
                href="/profile"
                className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-md hover:bg-indigo-700 font-semibold"
              >
                Set Preferences
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">Features</h2>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Automatic CV parsing (PDF/DOCX support)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Structured profile with skills, experience, and education</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Evidence tracking - know where each detail came from</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Editable profile fields and preferences</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>MongoDB storage for persistent data</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Location, language, and skill preferences</span>
              </li>
            </ul>
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600">
              Built with Next.js, FastAPI, MongoDB Atlas, and Pydantic v2
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
