'use client';

interface ExtractedTextPreviewProps {
  text: string;
}

export default function ExtractedTextPreview({ text }: ExtractedTextPreviewProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Extracted Text</h2>
      <div className="bg-gray-50 p-4 rounded-md max-h-96 overflow-y-auto">
        <pre className="text-sm whitespace-pre-wrap font-mono">{text}</pre>
      </div>
    </div>
  );
}
