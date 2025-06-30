import React from 'react';

function ResultDisplay({ result }) {
  if (!result) return null;

  const { document_type, is_duplicate, data } = result;

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-lg w-full max-w-2xl">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Processing Result</h3>
      <div className="space-y-3 text-gray-700">
        <p><strong>Document Type:</strong> <span className="font-mono bg-gray-100 px-2 py-1 rounded">{document_type}</span></p>
        <p><strong>Is Duplicate:</strong> <span className={`font-mono px-2 py-1 rounded ${is_duplicate ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>{String(is_duplicate)}</span></p>
        {data && (
          <div>
            <h4 className="font-semibold mt-4">Extracted Data:</h4>
            <pre className="bg-gray-800 text-white p-4 rounded-md mt-2 overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultDisplay;
