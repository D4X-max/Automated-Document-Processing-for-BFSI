import React from 'react';
import Header from './components/Header';
import UploadForm from './components/UploadForm';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <Header />
      <main className="container mx-auto px-6 py-12 flex justify-center">
        <UploadForm />
      </main>
    </div>
  );
}

export default App;

