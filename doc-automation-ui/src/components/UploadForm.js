import React, { useState } from 'react';
import axios from 'axios';
import ResultDisplay from './ResultDisplay';

function UploadForm() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingResult, setProcessingResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
    setProcessingResult(null); // Clear previous results
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Please select a file first.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setProcessingResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/v1/process_document",
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setProcessingResult(response.data);
    } catch (err) {
      // --- THIS IS THE IMPROVED ERROR HANDLING BLOCK ---
      // It looks inside the error to find a specific message from the backend.
      let errorMessage = "An unknown error occurred. Please check the console.";
      if (err.response && err.response.data && err.response.data.detail) {
        // Use the specific error message from our FastAPI backend
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      console.error(err);
      // --------------------------------------------------
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
        <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center">Upload Your Document</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input 
              type="file" 
              onChange={handleFileSelect} 
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
              accept="image/png, image/jpeg, image/jpg"
            />
          </div>
          <button 
            type="submit" 
            disabled={isLoading || !selectedFile}
            className="w-full bg-violet-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-violet-700 disabled:bg-gray-400 transition duration-300"
          >
            {isLoading ? 'Processing...' : 'Process Document'}
          </button>
        </form>
        {error && <p className="text-red-500 text-center mt-4">{error}</p>}
      </div>

      {isLoading && <div className="mt-8 text-violet-600">Loading...</div>}

      <ResultDisplay result={processingResult} />
    </div>
  );
}

export default UploadForm;
